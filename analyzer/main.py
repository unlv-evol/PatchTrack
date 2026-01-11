"""PatchTrack main analyzer module.

Provides the PatchTrack class for classifying patches from ChatGPT against
GitHub pull requests, aggregating results, and generating visualizations.

Logging Configuration:
    The module uses Python's logging package. To configure logging output:
    
    import logging
    pt = PatchTrack(tokens)
    
    # Set logging level
    pt.set_verbose_mode(True)   # INFO level
    pt.set_verbose_mode(False)  # WARNING level
    
    # Or configure logging handler manually
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    pt.logger.addHandler(handler)
"""

import difflib
import glob
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from . import aggregator
from . import analysis
from . import classifier
from . import common
from . import constant
from . import helpers

# Directory and path constants
DEFAULT_DATA_DIR = 'data/'
DEFAULT_RESULTS_DIR = 'data/classified/'
DEFAULT_PATCHES_DIR = 'data/patches/'
JSON_PATTERN = '*_pr_sharings.json'

# Classification constants
CLASS_PATCH_APPLIED = 'PA'
CLASS_PATCH_NOT_APPLIED = 'PN'
CLASS_NOT_EXISTING = 'NOT EXISTING'
CLASS_CANNOT_CLASSIFY = 'CC'
CLASS_ERROR = 'ERROR'
CLASS_OTHER_EXT = 'OTHER EXT'

# GitHub API constants
GITHUB_API_BASE = 'https://api.github.com'
GITHUB_WEB_BASE = 'https://github.com'
PR_COMMITS_PER_PAGE = 100
PR_FILES_PER_PAGE = 100
MIN_COMMITS_THRESHOLD = 100
MIN_REVIEWS_THRESHOLD = 1

# Similarity and processing constants
DEFAULT_NGRAM_SIZE = 4
MIN_EXT_THRESHOLD = 1


class PatchTrack:
    def __init__(self, token_list: List[str]) -> None:
        """Initialize PatchTrack analyzer.

        Args:
            token_list: List of GitHub API tokens.
        """
        self.token_list = token_list
        self.token_counter = 0

        # Metadata
        self.main_line = "GitHub"
        self.variant = "ChatGPT"

        # Data storage
        self.repo_data: List[Any] = []
        self.result_dict: Dict[str, Any] = {}
        self.prs: List[str] = []
        self.pr_classifications: Dict[str, Any] = {}

        # Directory paths
        self.data_dir = DEFAULT_DATA_DIR
        self.main_dir_results = DEFAULT_RESULTS_DIR
        self.repo_dir_files = DEFAULT_PATCHES_DIR

        # DataFrame results
        self.df_files_classes: Optional[pd.DataFrame] = None
        self.df_patch_classes: Optional[pd.DataFrame] = None
        self.df_patches: Optional[pd.DataFrame] = None

        # Logging configuration
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def set_main_dir_results(self, directory: str) -> None:
        """Set output directory for classification results."""
        self.main_dir_results = directory

    def set_repo_dir_files(self, directory: str) -> None:
        """Set directory for patch files."""
        self.repo_dir_files = directory

    def set_prs(self, prs: List[int]) -> None:
        """Set list of PR numbers to process."""
        self.prs = [str(pr) for pr in prs]

    def get_results(self) -> Dict[str, Any]:
        """Get classification results dictionary."""
        return self.result_dict

    def set_verbose_mode(self, mode: bool = True) -> None:
        """Set logging level based on verbose mode."""
        level = logging.INFO if mode else logging.WARNING
        self.logger.setLevel(level)

    def get_df_patches(self, num_rows: int = -1) -> Optional[pd.DataFrame]:
        """Get patches dataframe, optionally limited to num_rows."""
        if self.df_patches is None:
            return None
        if num_rows == -1:
            return self.df_patches
        if num_rows > self.df_patches.shape[0]:
            print(f'DataFrame contains only {self.df_patches.shape[0]} rows.')
        return self.df_patches.head(num_rows)

    def get_df_file_classes(self, num_rows: int = -1) -> Optional[pd.DataFrame]:
        """Get file classifications dataframe, optionally limited to num_rows."""
        if self.df_files_classes is None:
            return None
        if num_rows == -1:
            return self.df_files_classes
        if num_rows > self.df_files_classes.shape[0]:
            print(f'DataFrame contains only {self.df_files_classes.shape[0]} rows.')
        return self.df_files_classes.head(num_rows)

    def get_df_patch_classes(self, num_rows: int = -1) -> Optional[pd.DataFrame]:
        """Get patch classifications dataframe, optionally limited to num_rows."""
        if self.df_patch_classes is None:
            return None
        if num_rows == -1:
            return self.df_patch_classes
        if num_rows > self.df_patch_classes.shape[0]:
            print(f'DataFrame contains only {self.df_patch_classes.shape[0]} rows.')
        return self.df_patch_classes.head(num_rows)
        
    def prepare_data(self) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Prepare data by fetching and filtering projects and PRs.

        Returns:
            Tuple of (pr_project_pair, pair_project) mappings.
        """
        try:
            self.logger.info("Preparing data... please wait...")
            df, projects, merged_prs = self._get_projects()
            project_filter, projects_clean, prs_clean = self._filter_projects(projects, merged_prs)
            chatgpt_skip_prs = self._fetch_chatgpt_data(df, prs_clean)
            pr_project_pair, pair_project = self._fetch_github_data(prs_clean, chatgpt_skip_prs, self.token_list, self.token_counter)

            self.logger.info("Preparing data......COMPLETED!")
            return pr_project_pair, pair_project
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            raise

    def _get_projects(self) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """Retrieve projects and merged PR URLs from JSON files.

        Returns:
            Tuple of (dataframe, project_list, merged_pr_urls).
        """
        self.logger.info("Retrieving project details....")
        json_pattern = os.path.join(self.data_dir, JSON_PATTERN)
        file_list = glob.glob(json_pattern)

        dfs = []
        for file in file_list:
            with open(file) as f:
                json_data = pd.json_normalize(json.loads(f.read()))
                json_data['site'] = file.rsplit("/", 1)[-1]
            dfs.append(json_data)
        df = pd.concat(dfs)

        merged_prs = []
        for item in df['Sources']:
            for source in item:
                if source['State'] == 'MERGED':
                    merged_prs.append(source['URL'])

        projects = helpers.unique([pr.split('/pull/')[0] for pr in merged_prs])

        self.logger.info("Retrieving project details....COMPLETED!")
        return df, projects, merged_prs

    def _filter_projects(self, projects: List[str], merged_prs: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Filter projects by commit and review thresholds.

        Args:
            projects: List of GitHub project URLs.
            merged_prs: List of merged PR URLs.

        Returns:
            Tuple of (filtered_projects, clean_projects, clean_prs).
        """
        self.logger.info(f"Filter projects....criteria: {MIN_COMMITS_THRESHOLD} commits, {MIN_REVIEWS_THRESHOLD} review")
        
        project_filter = []
        for project in projects:
            part = project.split('github.com/')
            try:
                commits_url = f'{part[0]}api.github.com/repos/{part[1]}/commits?per_page={PR_COMMITS_PER_PAGE}'
                fetch_commits = helpers.api_request(commits_url, self.token_list[0])
                if len(fetch_commits) >= MIN_COMMITS_THRESHOLD:
                    project_filter.append(project)
            except Exception as e:
                self.logger.warning(f"Skipping project: {e}")

        prs_clean = []
        for project in project_filter:
            for pr in merged_prs:
                pr_part = pr.split('/pull/')
                if project == pr_part[0]:
                    project_part = project.split('github.com/')
                    try:
                        comments_url = f"{GITHUB_API_BASE}/repos/{project_part[1]}/pulls/{pr_part[1]}/reviews"
                        fetch_comments = helpers.api_request(comments_url, self.token_list[0])
                        if len(fetch_comments) >= MIN_REVIEWS_THRESHOLD:
                            prs_clean.append(pr)
                    except Exception as e:
                        self.logger.warning(f"Skipping PR: {e}")

        prs_clean = helpers.unique(prs_clean)
        projects_clean = helpers.unique([pr.split('/pull/')[0] for pr in prs_clean])

        self.logger.info("Filter projects....COMPLETED")
        return project_filter, projects_clean, prs_clean
    
    def _fetch_chatgpt_data(self, df: pd.DataFrame, prs_clean: List[str]) -> List[str]:
        """Fetch ChatGPT conversation patches and store locally.

        Args:
            df: DataFrame containing source data.
            prs_clean: List of clean PR URLs to process.

        Returns:
            List of ChatGPT PR URLs with 404 errors (to skip).
        """
        self.logger.info("Fetching ChatGPT data.......")
        chatgpt_skip_prs = []
        
        for sources in df['Sources']:
            for source in sources:
                if source['URL'] not in prs_clean or source['State'] != 'MERGED':
                    continue

                try:
                    if not source.get('ChatgptSharing'):
                        continue

                    for chat_sharing in source['ChatgptSharing']:
                        for prompt in chat_sharing.get('Conversations', []):
                            for code_item in prompt.get('ListOfCode', []):
                                if not code_item.get('Content'):
                                    continue

                                extension = constant.EXTENSIONS.get(code_item['Type'], 'txt')
                                repo_name = source['RepoName']
                                storage_dir = f'{self.repo_dir_files}{repo_name}/{source["Number"]}/chatgpt/'

                                os.makedirs(storage_dir, exist_ok=True)
                                
                                count = len([f for f in os.listdir(storage_dir) if f.startswith('patch-')]) + 1
                                patch_path = f'{storage_dir}patch-{count}.{extension}'
                                with open(patch_path, 'w') as f:
                                    f.write(code_item['Content'])

                except Exception as e:
                    chatgpt_skip_prs.append(source['URL'])
                    self.logger.warning(f"Skipping ChatGPT data: {e} - {source['URL']}")

        self.logger.info("Fetching ChatGPT data.......COMPLETED!")
        return chatgpt_skip_prs

    def _fetch_github_data(self, prs_clean: List[str], skip_prs: List[str], token_list: List[str], token_idx: int) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Fetch GitHub patch files for PRs.

        Args:
            prs_clean: List of PR URLs to process.
            skip_prs: List of PR URLs to skip.
            token_list: List of GitHub API tokens.
            token_idx: Current token index.

        Returns:
            Tuple of (pr_project_pair, pair_project) mappings.
        """
        self.logger.info("Fetching GITHUB data.......")
        pr_project_pair: Dict[str, Any] = {}
        pair_project: Dict[str, str] = {}

        token_length = len(token_list)

        for pr_url in prs_clean:
            if pr_url in skip_prs:
                continue

            repo_parts = pr_url.split('https://github.com/')[1].split('/pull/')
            project = repo_parts[0]
            pr_nr = repo_parts[1]

            pr_project_pair[pr_nr] = {}
            pair_project[pr_nr] = project

            try:
                if token_idx >= token_length:
                    token_idx = 0

                files_url = f'{GITHUB_API_BASE}/repos/{project}/pulls/{pr_nr}/files?page=1&per_page={PR_FILES_PER_PAGE}'
                pr_files, token_idx = helpers.get_response(files_url, token_list, token_idx)
                token_idx += 1

                pr_data = []
                for idx, file in enumerate(pr_files, 1):
                    try:
                        patch_content = file.get('patch', '')
                        status = file.get('status', '')
                        storage_dir = f'{self.repo_dir_files}{project}/{pr_nr}/github/'

                        os.makedirs(storage_dir, exist_ok=True)
                        patch_path = f'{storage_dir}patch-{idx}.patch'
                        
                        with open(patch_path, 'w') as f:
                            f.write(patch_content)

                        pr_data.append({
                            'filepath': patch_path,
                            'status': status
                        })
                    except Exception as e:
                        self.logger.warning(f"Skipping patch: {e}")

                pr_project_pair[pr_nr][project] = pr_data

            except Exception as e:
                self.logger.error(f"Error fetching PR data: {pr_url} - {e}")

        self.logger.info("Fetching GITHUB data.......COMPLETED!")
        return pr_project_pair, pair_project
    
    def build_pr_project_pairs(self) -> List[Dict[str, str]]:
        """Build PR to project mappings from directory structure.

        Returns:
            List of dicts mapping PR numbers to projects.
        """
        self.logger.info("Building PR <> Project Pair...")
        result = []
        
        for root, dirs, _ in os.walk(self.repo_dir_files):
            depth = root[len(self.repo_dir_files):].count(os.sep)
            if depth == 1:
                for dir_name in dirs:
                    full_path = os.path.join(root, dir_name)
                    parts = full_path.split('/')
                    result.append({parts[-1]: f'{parts[-3]}/{parts[-2]}'})

        self.logger.info("Building PR <> Project Pair......COMPLETED!")
        return result

    def read_file(self, file_path: str) -> str:
        """Read file contents with latin-1 encoding.

        Args:
            file_path: Path to file to read.

        Returns:
            File contents as string.
        """
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

    def compare_text_with_patch(self, text: str, patch_content: str) -> float:
        """Calculate similarity between text and patch using SequenceMatcher.

        Args:
            text: Original text content.
            patch_content: Patch content to compare.

        Returns:
            Similarity ratio (0-1).
        """
        return difflib.SequenceMatcher(None, text, patch_content).ratio()

    def _process_missing_chatgpt_dir(self, pr_nr: str, project: str, patch_file_path: str) -> List[Dict[str, Any]]:
        """Handle case when ChatGPT directory does not exist.

        Returns:
            List with single result dict for NOT EXISTING classification.
        """
        result: List[Dict[str, Any]] = []
        result_item = {
            'similarityRatio': 0.0,
            'patchClass': CLASS_NOT_EXISTING,
            'destPath': patch_file_path,
            'patchPath': patch_file_path,
            'destLOC': 0,
            'patchLOC': 0,
            'PrLink': f'{GITHUB_WEB_BASE}/{project}/pull/{pr_nr}'
        }
        result.append(result_item)
        return result

    def _process_patch_pair(self, text_file_path: str, patch_file_path: str, file_ext: int, pr_nr: str, project: str) -> Optional[Dict[str, Any]]:
        """Process a single patch-text file pair.

        Returns:
            Result dict or None on error.
        """
        try:
            text_loc = helpers.count_loc(text_file_path)
            patch_loc = helpers.count_loc(patch_file_path)

            if file_ext <= MIN_EXT_THRESHOLD:
                return {
                    'similarityRatio': 0.0,
                    'patchClass': CLASS_OTHER_EXT,
                    'destPath': text_file_path,
                    'destLOC': text_loc,
                    'patchPath': patch_file_path,
                    'patchLOC': patch_loc,
                    'PrLink': f'{GITHUB_WEB_BASE}/{project}/pull/{pr_nr}',
                    'type': 'N/A'
                }

            common.ngram_size = 1
            patch_loader_obj, source_loader_obj = classifier.process_patch(patch_file_path, text_file_path, 'patch', file_ext)
            
            added = patch_loader_obj.added()
            match_items = source_loader_obj.match_items()
            source_hashes = source_loader_obj.source_hashes()

            hunk_matches = classifier.find_hunk_matches_w_important_hash(match_items, CLASS_PATCH_APPLIED, added, source_hashes)
            similarity_ratio = classifier.cal_similarity_ratio(source_hashes, added)

            hunk_classes = []
            for _ in hunk_matches:
                hunk_class = classifier.classify_hunk('', hunk_matches[_]['class'])
                hunk_classes.append(hunk_class)

            return {
                'type': 'ADDED',
                'destPath': text_file_path,
                'destLOC': text_loc,
                'patchPath': patch_file_path,
                'patchLOC': patch_loc,
                'PrLink': f'{GITHUB_WEB_BASE}/{project}/pull/{pr_nr}',
                'similarityRatio': round(similarity_ratio, 2),
                'hunkMatches': hunk_matches,
                'patchClass': classifier.classify_patch(hunk_classes)
            }

        except Exception as e:
            self.logger.error(f'Error processing patch pair: {e}')
            return None

    def classify(self, pr_project_pair: Dict[str, str]) -> None:
        """Classify patches for all PRs.

        Args:
            pr_project_pair: Mapping of PR numbers to projects.
        """
        self.logger.info(f'Starting classification for {self.main_line} -> {self.variant}...')
        start_time = time.time()

        for pr_nr, project in pr_project_pair.items():
            root_directory = f'{self.repo_dir_files}{project}/'
            chatgpt_dir = f'{root_directory}{pr_nr}/chatgpt/'
            github_dir = f'{root_directory}{pr_nr}/github/'

            self.result_dict[pr_nr] = {}

            if not os.path.exists(chatgpt_dir):
                github_files = [f for f in os.listdir(github_dir) if not f.startswith('.')]
                patch_path = f'{github_dir}{github_files[0]}'
                self.result_dict[pr_nr][patch_path] = {
                    'result': self._process_missing_chatgpt_dir(pr_nr, project, patch_path)
                }
                continue

            try:
                chatgpt_files = [f for f in os.listdir(chatgpt_dir) if not f.startswith('.')]
                github_files = [f for f in os.listdir(github_dir) if not f.startswith('.')]

                for text_file in chatgpt_files:
                    text_path = os.path.join(chatgpt_dir, text_file)
                    file_ext = helpers.get_file_type(text_path)
                    self.result_dict[pr_nr][text_path] = {}
                    result_list: List[Dict[str, Any]] = []

                    for patch_file in github_files:
                        patch_path = os.path.join(github_dir, patch_file)
                        result = self._process_patch_pair(text_path, patch_path, file_ext, pr_nr, project)
                        
                        if result is None:
                            result = {
                                'similarityRatio': 0.0,
                                'patchClass': CLASS_ERROR,
                                'destPath': text_path,
                                'destLOC': helpers.count_loc(text_path),
                                'patchPath': patch_path,
                                'patchLOC': helpers.count_loc(patch_path),
                                'PrLink': f'{GITHUB_WEB_BASE}/{project}/pull/{pr_nr}'
                            }
                        result_list.append(result)

                    self.result_dict[pr_nr][text_path]['result'] = result_list

            except Exception as e:
                self.logger.error(f"Error processing PR {pr_nr}: {e}")

        self.pr_classifications = aggregator.final_class(self.result_dict)
        _ = aggregator.count_all_classifications(self.pr_classifications)

        duration = time.time() - start_time
        self.logger.info(f'Classification finished.')
        self.logger.info(f'Classification Runtime: {duration:.2f}s')

        common.pickleFile(f"{self.main_dir_results}_{self.main_line}_results", 
                         [self.result_dict, self.pr_classifications, _, duration])
            

    def run_classification(self, pr_project_pairs: Dict[str, str]) -> None:
        """Run full classification pipeline.

        Args:
            pr_project_pairs: Mapping of PR numbers to projects.
        """
        print('=' * 70)
        self.classify(pr_project_pairs)
        self.create_dataframes()
        print('=' * 70)
        self.visualize_results()

    def create_dataframes(self) -> None:
        """Create DataFrames from classification results."""
        file_results: List[List[Any]] = []
        patch_results: List[List[Any]] = []

        for pr, files_dict in self.result_dict.items():
            for file_path, file_data in files_dict.items():
                for item in file_data['result']:
                    is_interesting = 1 if item.get('patchClass') == CLASS_PATCH_APPLIED else 0
                    patch_type = item.get('type', 'None')
                    
                    file_results.append([
                        self.main_line,
                        self.variant,
                        pr,
                        file_path,
                        item.get('PrLink', ''),
                        item.get('destLOC', 0),
                        item.get('patchPath', ''),
                        item.get('patchLOC', 0),
                        patch_type,
                        item.get('similarityRatio', 0.0),
                        item.get('patchClass', ''),
                        is_interesting
                    ])

                # PR-level result (use first result for link)
                if file_data['result']:
                    pr_class = self.pr_classifications[pr]['class']
                    pr_interesting = 1 if pr_class == CLASS_PATCH_APPLIED else 0
                    patch_results.append([
                        self.main_line,
                        self.variant,
                        pr,
                        file_data['result'][0].get('PrLink', ''),
                        pr_class,
                        pr_interesting
                    ])

        columns_files = ['GitHub', 'ChatGPT', 'Pull Request', 'File Path', 'PR Link',
                        'ChatGPT LOC', 'GitHub Patch Path', 'GitHub LOC', 'Operation',
                        'Similarity (%)', 'File Classification', 'Interesting']
        columns_patches = ['GitHub', 'ChatGPT', 'Pull Request', 'PR Link',
                          'Patch Classification', 'Interesting']

        self.df_files_classes = pd.DataFrame(file_results, columns=columns_files)
        self.df_files_classes = self.df_files_classes.sort_values(
            by=['Pull Request', 'Interesting'], ascending=False)

        self.df_patch_classes = pd.DataFrame(patch_results, columns=columns_patches)
        self.df_patch_classes = self.df_patch_classes.sort_values(
            by='Interesting', ascending=False)

    def print_results(self) -> None:
        """Print classification results in human-readable format."""
        print('\nClassification Results:')
        for pr in self.result_dict:
            print(f'\n{self.main_line} -> {self.variant}')
            print(f'Pull Request: {pr}')
            print('File Classifications:')

            for file_path in self.result_dict[pr]:
                result_data = self.result_dict[pr][file_path].get('result', [])
                for item in result_data:
                    print(f'  {file_path}')
                    print(f'    Class: {item.get("patchClass", "")}')
                    if item.get('type'):
                        print(f'    Operation: {item["type"]}')

            if pr in self.pr_classifications:
                print(f'PR Classification: {self.pr_classifications[pr]["class"]}')

    def visualize_results(self) -> None:
        """Generate and display visualization plots for results."""
        self.logger.info(f'Generating plots for {self.main_line} -> {self.variant}...')

        class_counts: Dict[str, int] = {
            CLASS_PATCH_APPLIED: 0,
            CLASS_PATCH_NOT_APPLIED: 0,
            CLASS_CANNOT_CLASSIFY: 0,
            CLASS_NOT_EXISTING: 0,
            CLASS_ERROR: 0
        }

        for pr in self.pr_classifications:
            pr_class = self.pr_classifications[pr].get('class', '')
            if pr_class in class_counts:
                class_counts[pr_class] += 1

        totals_list = [
            class_counts[CLASS_PATCH_APPLIED],
            class_counts[CLASS_PATCH_NOT_APPLIED],
            class_counts[CLASS_NOT_EXISTING],
            class_counts[CLASS_CANNOT_CLASSIFY],
            class_counts[CLASS_ERROR]
        ]

        analysis.all_class_bar(totals_list, True)
        