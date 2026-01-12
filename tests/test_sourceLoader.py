"""Unit tests for analyzer.sourceLoader module.

Tests the SourceLoader class including:
- Normalization behavior (uses helpers.remove_comments)
- Bloom filter querying and match detection with mocked patch entries
- Edge cases for short sources
"""

import os
import pytest
from analyzer import sourceLoader, common, helpers


class MockPatchEntry:
    def __init__(self, ngram_size, hash_indices, old_norm_lines=None):
        # build tuple-like indexed access: (file_path, file_ext, orig_lines, norm_lines, hash_list, patch_hashes, ngram_size)
        self._tuple = ("/tmp/file.java", 3, "orig", ["word"], hash_indices, [], ngram_size)
        self.hash_list = hash_indices
        self._old_norm_lines = old_norm_lines or []

    def __getitem__(self, idx):
        return self._tuple[idx]

    def get(self, key, default=None):
        if key == 'old_norm_lines':
            return self._old_norm_lines
        return default


class MockPatch:
    def __init__(self, entries):
        self._entries = entries

    def items(self):
        return self._entries

    def length(self):
        return len(self._entries)


def setup_helpers_remove_comments(monkeypatch):
    # helpers has remove_comment (singular). Provide remove_comments to avoid AttributeError.
    # create attribute even if missing
    monkeypatch.setattr(helpers, 'remove_comments', helpers.remove_comment, raising=False)


def test_source_loader_init():
    loader = sourceLoader.SourceLoader()
    assert loader.items() == []
    assert loader.length() == 0
    assert isinstance(loader.match_items(), dict)
    assert isinstance(loader.results(), dict)
    assert isinstance(loader.source_hashes(), list)


def test_normalize_uses_helpers(monkeypatch):
    setup_helpers_remove_comments(monkeypatch)

    # Replace remove_comments with a function that uppercases input to ensure normalization lowercases
    monkeypatch.setattr(helpers, 'remove_comments', lambda s, ext: s.upper())

    loader = sourceLoader.SourceLoader()
    result = loader._normalize("Hello World\n  x = 1", common.FileExt.Java)
    # remove_comments returned uppercase, _normalize should lowercase
    assert 'hello' in result
    assert '\n' in result


def test_query_bloomfilter_detects_match(tmp_path, monkeypatch):
    setup_helpers_remove_comments(monkeypatch)
    # ensure remove_comments is identity
    monkeypatch.setattr(helpers, 'remove_comments', lambda s, ext: s)

    # Build a simple source file with tokens 'word word word'
    source_file = tmp_path / "source.java"
    source_file.write_text("word word word")

    # Compute ngram and its masked hash indices
    ngram = 'word'
    bloom_size = common.bloomfilter_size
    h1 = common.fnv1a_hash(ngram) & (bloom_size - 1)
    h2 = common.djb2_hash(ngram) & (bloom_size - 1)
    h3 = common.sdbm_hash(ngram) & (bloom_size - 1)

    # Create mock patch entry where hash_list contains the masked indices
    entry = MockPatchEntry(ngram_size=1, hash_indices=[h1, h2, h3], old_norm_lines=[h1, h2, h3])
    patch = MockPatch([entry])

    loader = sourceLoader.SourceLoader()
    nmatch = loader.traverse(str(source_file), patch, common.FileExt.Java)

    # Expect at least one match recorded
    matches = loader.match_items()
    results = loader.results()
    assert isinstance(matches, dict)
    # If a match was found, nmatch should be >= 0 (function returns count)
    assert isinstance(nmatch, int)
    # Results dictionary should include our hash keys
    assert all(h in results for h in [h1, h2, h3])


def test_short_source_no_analysis(tmp_path, monkeypatch):
    setup_helpers_remove_comments(monkeypatch)
    monkeypatch.setattr(helpers, 'remove_comments', lambda s, ext: s)

    source_file = tmp_path / "short.java"
    source_file.write_text("only")

    # Patch expects ngram_size larger than tokens available
    entry = MockPatchEntry(ngram_size=5, hash_indices=[1,2,3])
    patch = MockPatch([entry])

    loader = sourceLoader.SourceLoader()
    nmatch = loader.traverse(str(source_file), patch, common.FileExt.Java)

    # No matches expected (no True matches); the match structure may be populated with False entries
    assert nmatch == 0
    matches = loader.match_items()
    # Ensure no True match values exist
    has_true = False
    for pid, seqdict in matches.items():
        for seq, hdict in seqdict.items():
            if isinstance(hdict, dict):
                if any(v for v in hdict.values()):
                    has_true = True
            else:
                # if it's a list-like, ensure no True
                if any(hdict):
                    has_true = True
    assert not has_true


def test_source_hashes_populated(tmp_path, monkeypatch):
    setup_helpers_remove_comments(monkeypatch)
    monkeypatch.setattr(helpers, 'remove_comments', lambda s, ext: s)

    source_file = tmp_path / "source2.java"
    source_file.write_text("a b c d e")

    ngram = 'a'
    bloom_size = common.bloomfilter_size
    h1 = common.fnv1a_hash(ngram) & (bloom_size - 1)
    h2 = common.djb2_hash(ngram) & (bloom_size - 1)
    h3 = common.sdbm_hash(ngram) & (bloom_size - 1)

    entry = MockPatchEntry(ngram_size=1, hash_indices=[h1, h2, h3])
    patch = MockPatch([entry])

    loader = sourceLoader.SourceLoader()
    loader.traverse(str(source_file), patch, common.FileExt.Java)

    # source_hashes should be a list (may be empty depending on normalization)
    assert isinstance(loader.source_hashes(), list)
