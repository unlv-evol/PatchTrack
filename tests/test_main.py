import os
import tempfile
from pathlib import Path

import pytest

from analyzer.main import PatchTrack, DEFAULT_DATA_DIR
from analyzer import common


def test_patchtrack_init_and_setters():
    pt = PatchTrack([])
    assert pt.token_list == []

    pt.set_main_dir_results('out/')
    assert pt.main_dir_results == 'out/'

    pt.set_repo_dir_files('rdir/')
    assert pt.repo_dir_files == 'rdir/'

    pt.set_prs([1, 2, 3])
    assert pt.prs == ['1', '2', '3']

    pt.set_verbose_mode(False)
    # logging level should be WARNING (30)
    assert pt.logger.level in (30,)


def test_get_df_when_none():
    pt = PatchTrack([])
    assert pt.get_df_patches() is None
    assert pt.get_df_file_classes() is None
    assert pt.get_df_patch_classes() is None


def test_read_file_and_compare(tmp_path):
    pt = PatchTrack([])
    p = tmp_path / "f.txt"
    p.write_text("hello world", encoding='latin-1')
    content = pt.read_file(str(p))
    assert 'hello' in content

    ratio = pt.compare_text_with_patch('abc', 'abcde')
    assert 0 < ratio <= 1


def test__process_missing_chatgpt_dir_fields():
    pt = PatchTrack([])
    res = pt._process_missing_chatgpt_dir('5', 'owner/repo', 'some/path')
    assert isinstance(res, list) and len(res) == 1
    item = res[0]
    assert item['patchClass'] == 'NOT EXISTING' or item['patchClass'] == 'NOT EXISTING'
    assert item['PrLink'].endswith('/owner/repo/pull/5')


def test_build_pr_project_pairs(tmp_path):
    # Create directory structure: repo_dir_files/project/pr/childdir
    base = tmp_path / 'repo_files'
    base_dir = base.as_posix() + '/'
    project = 'projX'
    pr = '123'
    child = 'github'

    (base / project / pr / child).mkdir(parents=True)

    pt = PatchTrack([])
    pt.set_repo_dir_files(base_dir)

    pairs = pt.build_pr_project_pairs()
    # Expect one mapping: {child: 'projX/123'}
    assert any(list(x.values())[0] == f'{project}/{pr}' for x in pairs)


def test_classify_missing_chatgpt_dir_creates_not_existing(tmp_path, monkeypatch):
    # Setup patch file under github dir, no chatgpt dir
    base = tmp_path / 'repo_files'
    base_dir = base.as_posix() + '/'
    project = 'projY'
    pr = '7'
    github = base / project / pr / 'github'
    github.mkdir(parents=True)
    patch_file = github / 'patch-1.patch'
    patch_file.write_text('dummy patch')

    pt = PatchTrack([])
    pt.set_repo_dir_files(base_dir)

    # Prevent writing pickle in classify (create attribute if missing)
    monkeypatch.setattr(common, 'pickleFile', lambda *a, **k: None, raising=False)

    # Patch aggregator.final_class to accept dict input (main.classify passes a dict)
    from analyzer import aggregator

    def fake_final(result_dict):
        # return a list of dicts keyed by PR id
        return [{p: {'class': aggregator.CLASS_NOT_EXISTING}} for p in result_dict.keys()]

    monkeypatch.setattr(aggregator, 'final_class', fake_final)

    pr_project_pair = {pr: project}
    pt.classify(pr_project_pair)

    assert pr in pt.result_dict
    # There should be a patch path key inside result_dict[pr]
    keys = list(pt.result_dict[pr].keys())
    assert any('patch-' in os.path.basename(k) for k in keys)

    # The stored classification should be NOT EXISTING for the entry
    first_key = keys[0]
    results = pt.result_dict[pr][first_key]['result']
    assert results[0]['patchClass'] == 'NOT EXISTING'
