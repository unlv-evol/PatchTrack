"""Patch classifier helpers.

This module contains helper functions used by the patch classification
pipeline. The refactor preserves original logic but improves readability
by adding type hints, docstrings, and removing commented-out code.
"""

from typing import Any, Dict, List, Tuple

from . import patchLoader as patch_loader
from . import sourceLoader as source_loader
from . import common
from . import constant


def process_patch(patch_path: str, dst_path: str, type_patch: str, file_ext: str) -> Tuple[Any, Any]:
    """Process a patch and its corresponding source traversal.

    This wraps `PatchLoader.traverse` and `SourceLoader.traverse`, preserving
    the original try/except logging behavior.

    Args:
        patch_path: Path to the patch file.
        dst_path: Path to the destination/source files.
        type_patch: Type of patch (e.g., buggy/fixed).
        file_ext: File extension being processed.

    Returns:
        Tuple of (patch_loader_instance, source_loader_instance).
    """
    common.ngram_size = constant.NGRAM_SIZE

    patch = patch_loader.PatchLoader()
    try:
        _ = patch.traverse(patch_path, type_patch, file_ext)
    except Exception as e:
        print("Error traversing patch:....", e)

    source = source_loader.SourceLoader()
    try:
        _ = source.traverse(dst_path, patch, file_ext)
    except Exception as e:
        print("Error traversing source (variant)....", e)

    return patch, source


def get_ext(filename: str) -> str:
    """Return the file extension for `filename`.

    If no extension is present this returns an empty string.
    """
    parts = filename.rsplit('.', 1)
    return parts[-1] if len(parts) == 2 else ''


def calculate_match_percentage(results: Dict[Any, Dict[str, Any]], hashes: Dict[Any, Any]) -> float:
    """Calculate percentage of matched items in `results`.

    Args:
        results: Mapping of items to a dict containing a boolean under key `'Match'`.
        hashes: Mapping used to collect matched or unmatched items (kept for parity).

    Returns:
        Percentage (0-100) of matched items. Returns 0 if there are no items.
    """
    total = 0
    matched = 0

    for h in results:
        total += 1
        if results[h].get('Match'):
            matched += 1
    return (matched / total) * 100 if total != 0 else 0.0


def find_hunk_matches(match_items: Dict[Any, Any], _type: str, important_hashes: List[Any], source_hashes: List[Tuple[Any, Any]]) -> Dict[Any, Any]:
    """Find matches between hunks using hashed values.

    Preserves original matching logic and return structure.
    """
    seq_matches: Dict[Any, Any] = {}

    for patch_nr in match_items:
        seq_matches[patch_nr] = {'sequences': {}, 'class': ''}
        for patch_seq in match_items[patch_nr]:
            seq_matches[patch_nr]['sequences'][patch_seq] = {
                'count': 0,
                'hash_list': list(match_items[patch_nr][patch_seq].keys())
            }

            for k in match_items[patch_nr][patch_seq]:
                if match_items[patch_nr][patch_seq][k]:
                    seq_matches[patch_nr]['sequences'][patch_seq]['count'] += 1

    match_bool = True

    for seq_nr in seq_matches:
        for seq in seq_matches[seq_nr]['sequences']:
            if seq_matches[seq_nr]['sequences'][seq]['count'] < 2:
                match_bool = False
                break

        _class = ''
        if _type == 'MO':
            _class = _type if match_bool else 'MC'
        elif _type == 'PA':
            _class = _type if match_bool else 'MC'

        seq_matches[seq_nr]['class'] = _class

    return seq_matches


def classify_hunk(class_patch: str, class_buggy: str) -> str:
    """Classify a single hunk based on patch and buggy classifications.
    """
    final_class = ''
    if class_buggy == 'MC' and class_patch == 'PA':
        final_class = 'PA'
    if class_buggy == 'PA' and class_patch == 'MC':
        final_class = 'PA'
    if class_buggy == 'MC' and class_patch == 'MC':
        final_class = 'PN'
    if class_patch == '' and class_buggy != '':
        final_class = class_buggy
    if class_patch != '' and class_buggy == '':
        final_class = class_patch
    if class_patch == '' and class_buggy == '':
        final_class = 'PN'
    return final_class


def classify_patch(hunk_classifications: List[str]) -> str:
    """Determine patch-level classification from hunk classifications.
    """
    na_total = 0
    ed_total = 0

    final_class = ''
    for i in range(len(hunk_classifications)):
        if hunk_classifications[i] == 'PA':
            ed_total += 1
        elif hunk_classifications[i] == 'PN':
            na_total += 1

    final_class = 'PN' if ed_total == 0 else 'PA'
    return final_class


def find_hunk_matches_w_important_hash(match_items: Dict[Any, Any], _type: str, important_hashes: List[Any], source_hashes: List[Tuple[Any, Any]]) -> Dict[Any, Any]:
    """Find hunk matches using important hashes feature.

    Preserves original behavior and return structure.
    """
    seq_matches: Dict[Any, Any] = {}
    test: List[Any] = []
    for lines in important_hashes:
        for line in lines:
            for each in line:
                for ngram, hash_list in source_hashes:
                    if each in ngram:
                        test.append(hash_list)

    important_hash_match = 0
    for patch_nr in match_items:
        match_bool = False
        seq_matches[patch_nr] = {'sequences': {}, 'class': ''}
        for patch_seq in match_items[patch_nr]:
            seq_matches[patch_nr]['sequences'][patch_seq] = {
                'count': 0,
                'hash_list': list(match_items[patch_nr][patch_seq].keys())
            }

            if seq_matches[patch_nr]['sequences'][patch_seq]['hash_list'] in test:
                seq_matches[patch_nr]['sequences'][patch_seq]['important'] = True
                important_hash_match += 1
                match_bool = True
            else:
                seq_matches[patch_nr]['sequences'][patch_seq]['important'] = False

            for k in match_items[patch_nr][patch_seq]:
                if match_items[patch_nr][patch_seq][k]:
                    seq_matches[patch_nr]['sequences'][patch_seq]['count'] += 1

        seq_matches[patch_nr]['class'] = _type if match_bool else 'MC'

    return seq_matches


def cal_similarity_ratio(source_hashes: List[Tuple[Any, Any]], added_lines_hashes: List[List[List[Any]]]) -> float:
    """Calculate similarity ratio between source hashes and added lines hashes.
    """
    count_matches: List[Any] = []

    for lines in added_lines_hashes:
        for line in lines:
            for each in line:
                for ngram, hash_list in source_hashes:
                    if each == ngram:
                        count_matches.append(ngram)

    s_hashes: List[Any] = [ngram for ngram, _ in source_hashes]

    try:
        unique_matches = list(set(count_matches))
        unique_source_hashes = list(set(s_hashes))
        per = (len(unique_matches) / len(unique_source_hashes)) * 100
        return per
    except Exception:
        return 0.0
