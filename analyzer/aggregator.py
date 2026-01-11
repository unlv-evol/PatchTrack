"""Analysis totals module for PatchTrack.

Provides functions to load, aggregate, and classify patch analysis results
into final decision categories based on per-file classifications.
"""

from typing import List, Dict, Any
import pickle
import operator
import os

# Classification type constants
CLASS_PATCH_APPLIED = 'PA'
CLASS_PATCH_NOT_APPLIED = 'PN'
CLASS_NOT_EXISTING = 'NE'
CLASS_CANNOT_CLASSIFY = 'CC'
CLASS_ERROR = 'ERROR'
CLASS_OTHER_EXT = 'OTHER EXT'

# All classification types
ALL_CLASSIFICATIONS = [CLASS_PATCH_APPLIED, CLASS_PATCH_NOT_APPLIED, CLASS_NOT_EXISTING,
                       CLASS_CANNOT_CLASSIFY, CLASS_ERROR]

# Totals directory
TOTALS_DIR = 'Repos_totals'


def read_totals(repo_file: str, mainline: str) -> Dict[str, Any]:
    """Load aggregated analysis results for a repository.

    Args:
        repo_file: Repository identifier.
        mainline: Branch specification in 'owner/repo' format.

    Returns:
        Dictionary containing aggregated analysis totals.
    """
    owner, repo = mainline.split('/')
    file_path = os.path.join(TOTALS_DIR, f"{repo_file}_{owner}_{repo}_totals.pkl")
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def _initialize_classification_counts() -> Dict[str, int]:
    """Initialize count dictionary for all classification types.

    Returns:
        Dictionary with all classification types set to 0.
    """
    return {
        CLASS_PATCH_APPLIED: 0,
        CLASS_NOT_EXISTING: 0,
        CLASS_CANNOT_CLASSIFY: 0,
        CLASS_PATCH_NOT_APPLIED: 0,
        CLASS_ERROR: 0
    }


def _determine_ultimate_class(counts: Dict[str, int]) -> str:
    """Determine final classification based on per-file counts.

    Priority:
    1. If PA present, return PA
    2. If PN present (no PA), return PN
    3. Otherwise return most frequent (CC, NE, or ERROR)

    Args:
        counts: Dictionary of classification counts.

    Returns:
        Final classification string.
    """
    if counts[CLASS_PATCH_APPLIED] > 0:
        return CLASS_PATCH_APPLIED

    if counts[CLASS_PATCH_NOT_APPLIED] > 0:
        return CLASS_PATCH_NOT_APPLIED

    # Return most frequent remaining class
    remaining = {
        CLASS_CANNOT_CLASSIFY: counts[CLASS_CANNOT_CLASSIFY],
        CLASS_NOT_EXISTING: counts[CLASS_NOT_EXISTING],
        CLASS_ERROR: counts[CLASS_ERROR]
    }
    return max(remaining.items(), key=operator.itemgetter(1))[0]


def final_class(result_dict: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute final classification for each pull request.

    Aggregates per-file classifications into a single PR-level classification
    using priority-based logic:
    - PA (Patch Applied) takes precedence if present
    - PN (Patch Not Applied) takes precedence if no PA but PN present
    - Otherwise, most frequent of CC/NE/ERROR

    Args:
        result_dict: List of dictionaries containing per-file analysis results.
                    Format: [{pr_id: {file: {result: [item, ...]}, ...}}, ...]

    Returns:
        List of dictionaries with aggregated totals and final classification.
    """
    pr_classes = []

    for pr_data in result_dict:
        pr_id, files_data = next(iter(pr_data.items()))
        pr_result = {pr_id: {}}

        counts = _initialize_classification_counts()
        project = ''

        for file_name, file_result in files_data.items():
            for item in file_result['result']:
                project = item['project']
                try:
                    patch_class = item['patchClass']
                    if patch_class == CLASS_OTHER_EXT or patch_class == CLASS_CANNOT_CLASSIFY:
                        counts[CLASS_CANNOT_CLASSIFY] += 1
                    elif patch_class == CLASS_NOT_EXISTING:
                        counts[CLASS_NOT_EXISTING] += 1
                    elif patch_class == CLASS_PATCH_APPLIED:
                        counts[CLASS_PATCH_APPLIED] += 1
                    elif patch_class == CLASS_PATCH_NOT_APPLIED:
                        counts[CLASS_PATCH_NOT_APPLIED] += 1
                    elif patch_class == CLASS_ERROR:
                        counts[CLASS_ERROR] += 1
                except (KeyError, ValueError):
                    counts[CLASS_ERROR] += 1

        ultimate_class = _determine_ultimate_class(counts)

        pr_result[pr_id] = {
            'totals': {
                'total_PA': counts[CLASS_PATCH_APPLIED],
                'total_NE': counts[CLASS_NOT_EXISTING],
                'total_CC': counts[CLASS_CANNOT_CLASSIFY],
                'total_PN': counts[CLASS_PATCH_NOT_APPLIED],
                'total_ERROR': counts[CLASS_ERROR]
            },
            'class': ultimate_class,
            'project': project
        }
        pr_classes.append(pr_result)

    return pr_classes


def count_all_classifications(pr_classes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count final classification distribution across all pull requests.

    Args:
        pr_classes: List of PR classification results from final_class().

    Returns:
        Dictionary with counts for each classification type.
    """
    class_counts = {
        CLASS_PATCH_APPLIED: 0,
        CLASS_CANNOT_CLASSIFY: 0,
        CLASS_PATCH_NOT_APPLIED: 0,
        CLASS_NOT_EXISTING: 0,
        CLASS_ERROR: 0
    }

    for pr_result in pr_classes:
        pr_id, pr_data = next(iter(pr_result.items()))
        final_classification = pr_data.get('class')

        if final_classification in class_counts:
            class_counts[final_classification] += 1

    return class_counts
