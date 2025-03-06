import time
import pandas as pd
from . import common
from . import helpers
from . import classifier
from . import totals
from . import analysis
from . import constant
# import common,helpers,classifier,totals,analysis,constant
import difflib
import os
import json,glob
from datetime import datetime
    
class PatchTrack:
    def __init__(self, params):
        # self.repo_file, self.main_line, self.variant, self.token_list = params
        self.token_list = params
        self.ct = 0
        self.main_line = "GitHub"
        self.variant = "ChatGPT"
        self.repo_data = []
        self.result_dict = {}
        self.data_dir = 'data/'
        
        # self.len_tokens = len(self.token_list)
        self.main_dir_results= '../data/classified/' 
        self.repo_dir_files ='../data/patches/'
         
        self.verbose = True
        
        self.pr_classifications = {}
        
    def setMainDirResults(self, directory):
        self.main_dir_results = directory
        
    def setRepoDirFiles(self, directory):
        self.repo_dir_files = directory
        
    def setPrs(self, prs):
        self.prs = []
        for pr in prs:
            self.prs.append(str(pr))
        
    def results(self):
        return self.result_dict

    def verboseMode(self, mode = True):
        self.verbose = mode
   
    def verbosePrint(self, text):
        if self.verbose:
            print(text)
    
    def df_patches(self, nr_patches=-1):
        if nr_patches ==-1:
            return self.df_patches
        else:
            if nr_patches > self.df_patches.shape[0]:
                print(f'The dataframe contain only {self.df_patches.shape[0]} rows. Printing only {self.df_patches.shape[0]} rows.')
            return self.df_patches.head(nr_patches)
    
    def df_file_class(self, nr_patches=-1):
        if nr_patches ==-1:
            return self.df_files_classes
        else:
            if nr_patches > self.df_files_classes.shape[0]:
                print(f'The dataframe contain only {self.df_files_classes.shape[0]} rows. Printing only {self.df_files_classes.shape[0]} rows.')
            return self.df_files_classes.head(nr_patches)
        
    def df_patch_class(self, nr_patches=-1):
        if nr_patches ==-1:
            return self.df_patch_classes
        else:
            if nr_patches > self.df_patch_classes.shape[0]:
                print(f'The dataframe contain only {self.df_patch_classes.shape[0]} rows. Printing only {self.df_patch_classes.shape[0]} rows.')
            return self.df_patch_classes.head(nr_patches)
        
    def prepare_data(self): 
        try:
            print("Preparing data... please wait...")
            #1.  get projects
            df, projects, merged_pullrequest = self.get_projects();
            #2. filter projects
            project_filter, projects_clean, pull_request_clean = self.filter_projects(projects, merged_pullrequest);
            #3. fetch chatgpt data
            chatgapt_link_404 = self.fetch_chatgpt_data(df,pull_request_clean)

            #4. fetch github data
            pr_project_pair, pair_project = self.fetch_github_data(pull_request_clean, chatgapt_link_404, self.token_list, self.ct)

            print("Preparing data......COMPLETED!")
        except Exception as e:
            print(e)
        return pr_project_pair, pair_project
    
    def get_projects(self):
        print("Retrieving project details....")
        json_pattern = os.path.join(self.data_dir, '*_pr_sharings.json')
        file_list = glob.glob(json_pattern)

        dfs = []
        for file in file_list:
            with open(file) as f:
                json_data = pd.json_normalize(json.loads(f.read()))
                json_data['site'] = file.rsplit("/", 1)[-1]
            dfs.append(json_data)
        df = pd.concat(dfs)

        # get merged pr url
        pull_request_merged = []
        for item in df['Sources']:
            for i in item:
                if i['State'] == 'MERGED':
                    pull_request_merged.append(i['URL'])

        # extract project name from merged pr url
        temp = []
        for pr in pull_request_merged:
            temp.append(pr.split('/pull/')[0])
        projects = helpers.unique(temp)

        print("Retrieving project details....COMPLETED!")
        return df, projects, pull_request_merged
    
    def filter_projects(self, projects, merged_pr):
        print("Filter projects....criteria: 100 commits, 1 review")
        # Filter `toy projects based on the following criteria
        # 2. At least 100 commits
        # 3. At least 1 review - this is pracific to pull request.
        # two_developer = []
        project_filter = []
        for project in projects:
            # constract api url
            part = project.split('github.com/')
            # at least 100 commits
            try:
                commits_url = f'{part[0]}api.github.com/repos/{part[1]}/commits?per_page=100'
                fetch_commits = helpers.api_request(commits_url, self.token_list[0])
                if len(fetch_commits) >= 100:
                    project_filter.append(project)
            except Exception as e:
                print("skipping...", e)

        # get the merged PRs that are part of the remainings project and perform 
        # PR specific filtering... i.e. PR should have at least 1 review
        # e.g url: https://api.github.com/repos/apache/kafka/pulls/14540/comments

        pull_request_clean = []
        for pf in project_filter:
            for pr in merged_pr:
                pr_part = pr.split('/pull/')
                if pf == pr_part[0]:
                    # at least 1 reviews
                    pf_part = pf.split('github.com/')
                    try:
                        comments_url = f"{part[0]}api.github.com/repos/{pf_part[1]}/pulls/{pr_part[1]}/reviews"
                        fetch_comments = helpers.api_request(comments_url, self.token_list[0])
                        if len(fetch_comments) >= 1:
                            pull_request_clean.append(pr)
                    except Exception as e:
                        print("skipping...", e)
        # total number of PRs that met the selection criteria 
        pull_request_clean = helpers.unique(pull_request_clean)

        # get clean projects
        temp = []
        for pr in pull_request_clean:
            temp.append(pr.split('/pull/')[0])
        projects_clean = helpers.unique(temp)

        print("Filter projects....COMPLETED")

        return project_filter, projects_clean, pull_request_clean
    
    def fetch_chatgpt_data(self, df, pull_request_clean):
        print("Fetching ChatGPT data.......")
        prompt_result = []
        pull_duration = []
        chatgapt_link_404 = []
        no_listofcode = []
        for element in df['Sources']:
            for i in element:
                if i['URL'] in pull_request_clean and i['State'] == 'MERGED':
                    mergedAt = datetime.strptime(str(i['MergedAt']), '%Y-%m-%dT%H:%M:%SZ')
                    createdAt = datetime.strptime(str(i['CreatedAt']), '%Y-%m-%dT%H:%M:%SZ')
                    pr_duration = (mergedAt - createdAt).days
                    pull_duration.append(pr_duration)
                    try:
                        count = 1
                        if i['ChatgptSharing']:
                            try:
                                conversation = i['ChatgptSharing'][0]['Conversations']
                            except:
                                chatgapt_link_404.append(i['URL'])
                    
                            for prompts in i['ChatgptSharing'][0]['Conversations']:
                                prompt_result.append(prompts['Prompt'])
                                try:
                                    code = prompts['ListOfCode']
                                    if len(code) == 0:
                                        no_listofcode.append(i['URL'])
                                except:
                                    no_listofcode.append(i['URL'])

                                for content in prompts['ListOfCode']:
                                    if content['Content']:
                                        if content['Type'] in constant.EXTENSIONS:
                                            extension = constant.EXTENSIONS[content['Type']]
                                        else:
                                            extension = "txt"
                                        # print(content['Content'])
                                        repo_name = i['RepoName'] 
                                        storage_dir = f'{self.repo_dir_files}{repo_name}/{i["Number"]}/chatgpt/'
                                        if not os.path.exists(storage_dir):
                                            os.makedirs(storage_dir)
                                            path = f'{storage_dir}patch-{count}.{extension}'
                                            with open(path, 'x') as patch:
                                                patch.writelines(content['Content'])
                                        else: 
                                            count = count + 1
                                            path = f'{storage_dir}patch-{count}.{extension}'
                                            with open(path, 'x') as patch:
                                                patch.writelines(content['Content'])

                    except Exception as e:
                        print("Skipping.... ", e, i['URL'])
        print("Fetching ChatGPT data.......COMPLETED!")
        return chatgapt_link_404

    def fetch_github_data(self, pullrequests, skip_pr, token_list, ct):
        print("Fetching GITHUB data.......")
        token_length = len(token_list)
        pr_poject_pair = {}
        pair_project = {}
        for pullrequest in pullrequests:
            # pull request to skip
            if pullrequest in skip_pr:
                # print(pullrequest)
                continue
            repo = pullrequest.split('https://github.com/')[1].split('/pull/')
            pr_nr = repo[1]
            pj_no = repo[0]
        
            pr_poject_pair[pr_nr] = {}
            pair_project[pr_nr] = pj_no
            try:
                
                # get files and patches
                if ct == token_length:
                    ct = 0
                #files_merged = f'{constant.GITHUB_API_BASE_URL}{mainline}/commits/{merge_commit_sha}'
                files_merged = f'https://api.github.com/repos/{repo[0]}/pulls/{repo[1]}/files?page=1&per_page=100'
                pullrequest_files_merged, ct = helpers.get_response(files_merged, token_list, ct)
                #print(pullrequest_files_merged)
                ct += 1
                pr_data = []
                try:
                    count = 1
                    for file in  pullrequest_files_merged:
                        try:
                            patch = file['patch']
                            status = file['status']
                            storage_dir = f'{self.repo_dir_files}{repo[0]}/{repo[1]}/github/'
                            if not os.path.exists(storage_dir):
                                os.makedirs(storage_dir)
                                path = f'{storage_dir}patch-{count}.patch'
                                with open(path, 'x') as file:
                                    file.writelines(patch)
                            else: 
                                count = count + 1
                                path = f'{storage_dir}patch-{count}.patch'
                                with open(path, 'x') as file:
                                    file.writelines(patch)
                            
                            files = {}
                            files['filepath'] = path
                            files['status'] =  status
                            pr_data.append(files)
                        except Exception as e:
                            print("Skipping this patch...")
                        
                except Exception as e:
                    print(e, pullrequest)
            except Exception as e:
                print("Error while trying to fetch pull request data....: ", pullrequest)
            pr_poject_pair[pr_nr][pj_no] = pr_data
        print("Fetching GITHUB data.......COMPLETED!")
        return pr_poject_pair, pair_project
    
    def build_pr_project_pairs(self) -> list[dict]:
        print("==================== Building PR <> Project Pair ==============================")
        result = []
        directory_list = []
        for root, dirs, files in os.walk(self.repo_dir_files):
            # Calculate the depth by counting the slashes in the root path
            depth = root[len(self.repo_dir_files):].count(os.sep)
            
            # Only include directories at depth 0 or 1 (i.e., two levels)
            if depth == 1:
                for dir_name in dirs:
                    full_path = os.path.join(root, dir_name)
                    # print(full_path)
                    directory_list.append(full_path)
                    # directory_list.append(full_path.split(splitter)[-2])
        for i in directory_list:
            sp = i.split('/')
            sp = { sp[-1]: f'{sp[-3]}/{sp[-2]}'}
            result.append(sp)
        print("==================== Successful! ==============================")
        return result


    def read_file(self,file_path):
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

    def compare_text_with_patch(self, text, patch_content):

        # Calculate similarity using cosine similarity or other methods
        # For simplicity, let's use the Levenshtein distance as an example
        similarity = difflib.SequenceMatcher(None, text, patch_content).ratio()

        return similarity

    def classify(self, pr_project_pair):
        self.verbosePrint(f'\nStarting classification for {self.main_line}, - , {self.variant}...')
        start = time.time()
        for pr_nr, project in pr_project_pair.items():
            root_directory = f'{self.repo_dir_files}{project}/'

            text_files_directory = f'{root_directory}{pr_nr}/chatgpt/'
            patch_files_directory = f'{root_directory}{pr_nr}/github/'

            self.result_dict[pr_nr] = {}
            # store result for iterating through this file
            result = []
            patch_file_path =''
            # check if chatgpt directory exist
            if not os.path.exists(text_files_directory):
                patch_file_names  = [file for file in os.listdir(patch_files_directory) if not file.startswith('.')]
                patch_file_path = f'{patch_files_directory}{patch_file_names[0]}'
                self.result_dict[pr_nr][patch_file_path] = {}
                result_mod = {}
                result_mod['similarityRatio'] = ''
                result_mod['patchClass'] = 'NOT EXISTING'
                result_mod['destPath'] = patch_file_path
                result_mod['patchPath'] = patch_file_path
                result_mod['destLOC'] = patch_LOC
                result_mod['patchLOC'] = patch_LOC
                result_mod['PrLink'] = f'https://github.com/{project}/pull/{pr_nr}'
                result.append(result_mod)
                self.result_dict[pr_nr][patch_file_path]['result'] = result
                continue

            try:
                # Loop through the original text files
                for text_file_name in [file for file in os.listdir(text_files_directory) if not file.startswith('.')]:
                    text_file_path = os.path.join(text_files_directory, text_file_name)
                    self.result_dict[pr_nr][text_file_path] = {}
                    file_ext = helpers.get_file_type(text_file_path)
                    text_LOC = helpers.count_LOC(text_file_path)

                    # Loop through the patch files
                    for patch_file_name in [file for file in os.listdir(patch_files_directory) if not file.startswith('.')]:
                        patch_file_path = os.path.join(patch_files_directory, patch_file_name)
                        patch_LOC = helpers.count_LOC(patch_file_path) 
                        try:
                            if file_ext > 1:
                                common.ngram_size = 1
                                
                                x_patch_patch, x_patch = classifier.process_patch(patch_file_path, text_file_path, 'patch', file_ext)
                                added = x_patch_patch.added()
                                match_items_patch = x_patch.match_items()
                                source_hashes = x_patch.source_hashes()
                                patch_hashes = x_patch_patch.hashes()

                                hunk_matches_patch = classifier.find_hunk_matches_w_important_hash(match_items_patch, 'PA', added, source_hashes)
                                similarity_ratio = classifier.cal_similarity_ratio(source_hashes, added)
                                
                                hunk_classifications = []
                                for patch_nr in hunk_matches_patch:
                                    class_buggy =''
                                    class_patch = hunk_matches_patch[patch_nr]['class']

                                    hunk_class = classifier.classify_hunk(class_buggy, class_patch)
                                    hunk_classifications.append(hunk_class)
                                
                                result_mod = {}
                                result_mod['type'] = 'ADDED'
                                result_mod['destPath'] = text_file_path
                                result_mod['destLOC'] = text_LOC
                                result_mod['patchPath'] = patch_file_path
                                result_mod['patchLOC'] = patch_LOC
                                result_mod['PrLink'] = f'https://github.com/{project}/pull/{pr_nr}'
                                result_mod['processBuggy'] = ''
                                result_mod['processPatch'] = x_patch
                                result_mod['hunkMatchesBuggy'] = ''
                                result_mod['similarityRatio'] = round(similarity_ratio, 2)
                                result_mod['hunkMatchesPatch'] = hunk_matches_patch
                                result_mod['patchClass'] = classifier.classify_patch(hunk_classifications)
                                result.append(result_mod)

                            else:
                                if file_ext <= 1:
                                    result_mod = {}
                                    result_mod['similarityRatio'] = 0.0
                                    result_mod['patchClass'] = 'OTHER EXT'
                                    result_mod['destPath'] = text_file_path
                                    result_mod['destLOC'] = text_LOC
                                    result_mod['patchPath'] = patch_file_path
                                    result_mod['patchLOC'] = patch_LOC
                                    result_mod['PrLink'] = f'https://github.com/{project}/pull/{pr_nr}'
                                    result.append(result_mod)
                                else:
                                    result_mod['similarityRatio'] = 0.0
                                    result_mod['patchClass'] = 'NOT EXISTING'
                                    result_mod['destPath'] = text_file_path
                                    result_mod['destLOC'] = text_LOC
                                    result_mod['PrLink'] = f'https://github.com/{project}/pull/{pr_nr}'
                                    result_mod['patchPath'] = ''
                                    result.append(result_mod)

                        except Exception as e:
                            result_mod = {}
                            result_mod['similarityRatio'] = 0.0
                            result_mod['patchClass'] = 'ERROR'
                            result_mod['destPath'] = text_file_path
                            result_mod['destLOC'] = text_LOC
                            result_mod['patchPath'] = patch_file_path
                            result_mod['patchLOC'] = patch_LOC
                            result_mod['PrLink'] = f'https://github.com/{project}/pull/{pr_nr}'
                            result.append(result_mod)
                            print('Exception thrown is: ', e)
                            print('File: ', text_file_path)                        

                    self.result_dict[pr_nr][text_file_path]['result'] = result
            except Exception as e:
                print("Some error........: ", e)

        self.pr_classifications = totals.final_class(self.result_dict)     
        all_counts = totals.count_all_classifications(self.pr_classifications)

        end = time.time()
        duration = end-start
        self.verbosePrint(f'Classification finished.')
        self.verbosePrint(f'Classification Runtime: {duration}')

        common.pickleFile(f"{self.main_dir_results}_{self.main_line}_results", [self.result_dict, self.pr_classifications, all_counts, duration])
            

    def run_classification(self, pr_project_pairs):
        print('======================================================================')
        self.classify(pr_project_pairs)
        self.createDf()
        print('======================================================================')
        print('======================================================================')
        self.visualizeResults()

    def createDf(self):
        df_data_files = []
        df_data_patches = []
        for pr, files in self.result_dict.items():
            for file, result in files.items():
                # print(result)
                for item in result['result']:
                    if item["patchClass"] in ['PA']:
                        df_data_files.append([self.main_line, self.variant, pr, file, item["PrLink"], item["destLOC"], item["patchPath"], item["patchLOC"], item["type"], item["similarityRatio"], item["patchClass"], 1])
                    else:
                        df_data_files.append([self.main_line, self.variant, pr, file, item["PrLink"], item["destLOC"], item["patchPath"], item["patchLOC"], 'None',item["similarityRatio"], item["patchClass"], 0])
                        
                if self.pr_classifications[pr]["class"] in ['PA']:
                    df_data_patches.append([self.main_line, self.variant, pr, result['result'][0]['PrLink'], self.pr_classifications[pr]["class"], 1])
                else:
                    df_data_patches.append([self.main_line, self.variant, pr, result['result'][0]['PrLink'], self.pr_classifications[pr]["class"], 0])

        self.df_files_classes = pd.DataFrame(df_data_files, columns = ['GitHub', 'ChatGPT', 'Pull Request', 'PrLink', 'ChatGPT Patch', 'ChatGPTPatchLOC', 'GitHub Patch', 'GitHubPatchLOC', 'Operation', 'Similarity(%)','File Classification', 'Interesting'])
        self.df_files_classes = self.df_files_classes.sort_values(by =  ['Pull Request', 'Interesting'], ascending=False)
        
        self.df_patch_classes = pd.DataFrame(df_data_patches, columns = ['GitHub', 'ChatGPT', 'Pull Request', 'PrLink', 'Patch Classification', 'Interesting'])
        self.df_patch_classes = self.df_patch_classes.sort_values(by ='Interesting', ascending=False) 
    
    def printResults(self):
        print('\nClassification results:')
        for pr in self.result_dict:
            print('\n')
            print(f'{self.main_line} -> {self.variant}')
            print(f'Pull request nr ==> {pr}')
#             print('\n')
            print('File classifications ==> ')
            for file in self.result_dict[pr]:
                if self.result_dict[pr][file]["result"]["patchClass"] in ['PA']:
                    print(f'\t {file}')
                    print(f'\t\t Operation - {self.result_dict[pr][file]["result"]["type"]}')
                    print(f'\t\t Class - {self.result_dict[pr][file]["result"]["patchClass"]}')
                else:
                    print(f'\t {file}')
                    print(f'\t\t Class - {self.result_dict[pr][file]["result"]["patchClass"]}')
            print(f'Patch classification ==> {self.pr_classifications[pr]["class"]}')
            
    def visualizeResults(self):
        
        print(f'\nBar plot of the patch classifications for {self.main_line} -> {self.variant}')
        total_PN = 0
        total_PA = 0
        total_CC = 0
        total_NE = 0
        total_ERROR = 0
        
        total_all = 0
        total_ed_all = 0
        total_na_all = 0

        for pr in self.pr_classifications:
            class_ = self.pr_classifications[pr]['class']
            if class_ == 'PA':
                total_PA += 1
            elif class_ == 'PN':
                total_PN += 1
            elif class_ == 'CC':
                total_CC += 1
            elif class_ =='NE':
                total_NE += 1
            elif class_ == 'ERROR':
                total_ERROR += 1
                
            total_mid = total_PA
            total_all += total_mid
            
        # total_total =len(self.prs)
        
        total_ed_all += total_PA
        total_na_all += total_PN

        totals_list = [total_PA, total_PN, total_NE, total_CC, total_ERROR]

        analysis.all_class_bar(totals_list, True)
        # analysis.all_class_pie(totals_list, self.repo_file, self.main_line, self.variant, True)
        