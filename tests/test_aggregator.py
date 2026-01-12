import os
import pickle
from typing import Dict, Any

import pytest

from analyzer import aggregator


def test_initialize_classification_counts():
    counts = aggregator._initialize_classification_counts()
    expected_keys = {
        'PA', 'NE', 'CC', 'PN', 'ERROR'
    }
    assert set(counts.keys()) == expected_keys
    assert all(isinstance(v, int) and v == 0 for v in counts.values())


def test_determine_ultimate_class_priorities():
    counts = {'PA': 1, 'PN': 2, 'CC': 0, 'NE': 0, 'ERROR': 0}
    assert aggregator._determine_ultimate_class(counts) == 'PA'

    counts = {'PA': 0, 'PN': 3, 'CC': 0, 'NE': 0, 'ERROR': 0}
    assert aggregator._determine_ultimate_class(counts) == 'PN'

    counts = {'PA': 0, 'PN': 0, 'CC': 2, 'NE': 1, 'ERROR': 0}
    assert aggregator._determine_ultimate_class(counts) == 'CC'


def make_pr_item(project: str, patch_class: str = None) -> Dict[str, Any]:
    item = {'project': project}
    if patch_class is not None:
        item['patchClass'] = patch_class
    return item


def test_final_class_basic_and_missing_fields():
    # Single PR, single file, PA
    result_dict = [
        {'pr1': {'fileA': {'result': [make_pr_item('proj1', 'PA')]}}}
    ]
    out = aggregator.final_class(result_dict)
    assert isinstance(out, list) and len(out) == 1
    pr_res = out[0]['pr1']
    assert pr_res['totals']['total_PA'] == 1
    assert pr_res['class'] == 'PA'
    assert pr_res['project'] == 'proj1'

    # Handle OTHER EXT treated as CC and missing patchClass increases ERROR
    result_dict = [
        {'pr2': {'fileB': {'result': [make_pr_item('proj2', aggregator.CLASS_OTHER_EXT), make_pr_item('proj2')]}}}
    ]
    out = aggregator.final_class(result_dict)
    pr_res = out[0]['pr2']
    # OTHER EXT counts toward CC
    assert pr_res['totals']['total_CC'] >= 1
    # Missing patchClass increments ERROR
    assert pr_res['totals']['total_ERROR'] >= 1


def test_count_all_classifications_counts():
    pr_classes = [
        {'p1': {'class': aggregator.CLASS_PATCH_APPLIED}},
        {'p2': {'class': aggregator.CLASS_PATCH_NOT_APPLIED}},
        {'p3': {'class': aggregator.CLASS_PATCH_APPLIED}},
    ]
    counts = aggregator.count_all_classifications(pr_classes)
    assert counts[aggregator.CLASS_PATCH_APPLIED] == 2
    assert counts[aggregator.CLASS_PATCH_NOT_APPLIED] == 1


def test_read_totals_uses_totals_dir(tmp_path, monkeypatch):
    # Prepare temp totals dir and pickle file
    tmpdir = tmp_path / "TotalsDir"
    tmpdir.mkdir()
    monkeypatch.setattr(aggregator, 'TOTALS_DIR', str(tmpdir))

    repo_file = 'repofile'
    mainline = 'owner/repo'
    fname = f"{repo_file}_owner_repo_totals.pkl"
    data = {'some': 'data'}
    with open(tmpdir / fname, 'wb') as f:
        pickle.dump(data, f)

    loaded = aggregator.read_totals(repo_file, mainline)
    assert loaded == data
