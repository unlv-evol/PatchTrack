import pytest

from analyzer import classifier
from analyzer import common
from analyzer import constant


def test_get_ext_with_extension():
    assert classifier.get_ext('file.py') == 'py'


def test_get_ext_no_extension():
    assert classifier.get_ext('Makefile') == ''


def test_get_ext_multiple_dots():
    assert classifier.get_ext('archive.tar.gz') == 'gz'


def test_get_ext_hidden_file():
    # For files like '.env', the implementation returns the part after the dot
    assert classifier.get_ext('.env') == 'env'


def test_calculate_match_percentage_empty():
    assert classifier.calculate_match_percentage({}, {}) == 0.0


def test_calculate_match_percentage_all_matched():
    results = {1: {'Match': True}, 2: {'Match': True}}
    assert classifier.calculate_match_percentage(results, {}) == pytest.approx(100.0)


def test_calculate_match_percentage_partial():
    results = {1: {'Match': True}, 2: {'Match': False}, 3: {'Match': True}}
    assert classifier.calculate_match_percentage(results, {}) == pytest.approx((2 / 3) * 100)


def test_find_hunk_matches_all_counts_ge_2():
    match_items = {
        0: {
            0: {'h1': True, 'h2': True},
            1: {'h3': True, 'h4': True}
        }
    }
    res = classifier.find_hunk_matches(match_items, 'MO', [], [])
    assert 0 in res
    assert res[0]['class'] == 'MO'
    assert res[0]['sequences'][0]['count'] == 2
    assert set(res[0]['sequences'][0]['hash_list']) == {'h1', 'h2'}


def test_find_hunk_matches_counts_less_than_2():
    match_items = {0: {0: {'h1': True, 'h2': False}, 1: {'h3': True}}}
    res = classifier.find_hunk_matches(match_items, 'MO', [], [])
    assert res[0]['class'] == 'MC'


def test_classify_hunk_various():
    assert classifier.classify_hunk('PA', 'MC') == 'PA'
    assert classifier.classify_hunk('MC', 'PA') == 'PA'
    assert classifier.classify_hunk('MC', 'MC') == 'PN'
    assert classifier.classify_hunk('', 'PA') == 'PA'
    assert classifier.classify_hunk('PA', '') == 'PA'
    assert classifier.classify_hunk('', '') == 'PN'


def test_classify_patch():
    assert classifier.classify_patch(['PN', 'PN']) == 'PN'
    assert classifier.classify_patch(['PN', 'PA']) == 'PA'
    assert classifier.classify_patch([]) == 'PN'


def test_find_hunk_matches_w_important_hash_match_and_nonmatch():
    # source_hashes contains an ngram 'x' with associated hash list ['hlist']
    source_hashes = [('x', ['hlist'])]
    important_hashes = [['x']]
    # match_items uses keys that will be converted to the seq hash_list ['hlist']
    match_items = {0: {0: {'hlist': True}, 1: {'other': True}}}

    res = classifier.find_hunk_matches_w_important_hash(match_items, 'MO', important_hashes, source_hashes)
    # seq 0 should be marked important because its hash_list ['hlist'] is present in test
    assert res[0]['sequences'][0]['important'] is True
    # seq 1 should not be important
    assert res[0]['sequences'][1]['important'] is False
    assert res[0]['class'] in ('MO', 'MC')


def test_cal_similarity_ratio_basic():
    source_hashes = [('a', [1]), ('b', [2]), ('c', [3])]
    added_lines_hashes = [[['a'], ['x']], [['b']]]
    per = classifier.cal_similarity_ratio(source_hashes, added_lines_hashes)
    assert per == pytest.approx((2 / 3) * 100)


def test_cal_similarity_ratio_empty_source():
    assert classifier.cal_similarity_ratio([], [[['a']]]) == 0.0


def test_process_patch_monkeypatched(monkeypatch):
    # Monkeypatch PatchLoader and SourceLoader used in classifier
    class DummyPatch:
        def __init__(self):
            self.traversed = False

        def traverse(self, patch_path, type_patch, file_ext):
            self.traversed = True
            return True

    class DummySource:
        def __init__(self):
            self.traversed = False

        def traverse(self, dst_path, patch, file_ext):
            self.traversed = True
            return True

    monkeypatch.setattr(classifier.patch_loader, 'PatchLoader', DummyPatch)
    monkeypatch.setattr(classifier.source_loader, 'SourceLoader', DummySource)

    # Ensure the function returns instances of our dummy classes and sets common.ngram_size
    p, s = classifier.process_patch('patchpath', 'dstpath', 'type', 'py')
    assert isinstance(p, DummyPatch)
    assert isinstance(s, DummySource)
    assert common.ngram_size == constant.NGRAM_SIZE
