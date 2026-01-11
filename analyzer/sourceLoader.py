"""Source file loader for patch analysis.

The SourceLoader class traverses source files, normalizes them (removes comments,
collapses whitespace), and uses Bloom filters (Replaced with temporary array of hash tables) to efficiently query for matches
against patches.
"""

import os
import sys
import time
from typing import Any, Dict, List, Tuple

from . import common
from . import helpers

try:
    import bitarray
except ImportError as err:
    print(err)
    sys.exit(-1)

# Magic number constants
MIN_FILE_EXT_TYPE = 2  # Minimum supported file extension type index
MAX_FILE_EXT_TYPE = 40  # Maximum supported file extension type index


class SourceLoader:
    """Loads and analyzes source files using Bloom filter-based patch matching.

    This class normalizes source files (removing comments and excess whitespace),
    builds Bloom filters, and detects matches against known patches.
    """

    def __init__(self) -> None:
        """Initialize the SourceLoader with empty data structures."""
        self._patch_list: List[Any] = []
        self._npatch: int = 0
        self._source_list: List[Any] = []
        self._nsource: int = 0
        self._match_dict: Dict[int, Any] = {}
        self._nmatch: int = 0
        self._bit_vector: bitarray.bitarray = bitarray.bitarray(common.bloomfilter_size)
        self._results: Dict[int, Dict[str, Any]] = {}
        self._source_hashes: List[Tuple[str, List[int]]] = []
        self._patch_hashes: List[Any] = []

    def traverse(self, source_path: str, patch: Any, file_ext: int) -> int:
        """Traverse source files and query against patches.

        Args:
            source_path: Path to a file or directory to analyze.
            patch: Patch object with items() and length() methods.
            file_ext: File extension type index (from FileExt class).

        Returns:
            The number of matches found.
        """
        common.verbose_print('[+] traversing source files')
        start_time = time.time()
        self._patch_list = patch.items()
        self._npatch = patch.length()

        if os.path.isfile(source_path):
            common.verbose_print(f'  [-] {source_path}: {file_ext}')
            if MIN_FILE_EXT_TYPE <= file_ext < MAX_FILE_EXT_TYPE:
                self._process(source_path, file_ext)
        elif os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    common.verbose_print(f'  [-] {file_path}: {file_ext}')
                    if MIN_FILE_EXT_TYPE <= file_ext < MAX_FILE_EXT_TYPE:
                        self._process(file_path, file_ext)

        elapsed_time = time.time() - start_time
        common.verbose_print(f'[+] {self._nmatch} possible matches ... {elapsed_time:.1f}s\n')
        return self._nmatch

    def _process(self, source_path: str, magic_ext: int) -> None:
        """Normalize a source file and build a Bloom filter for queries.

        Args:
            source_path: Path to the source file.
            magic_ext: File extension type index.
        """
        with open(source_path, 'r') as source_file:
            source_orig_lines = source_file.read()

        source_norm_lines = self._normalize(source_orig_lines, magic_ext)
        self._query_bloomfilter(source_norm_lines, magic_ext)

    def _normalize(self, source: str, file_ext: int) -> str:
        """Normalize a source file by removing comments and whitespace.

        Args:
            source: The source code as a string.
            file_ext: File extension type index.

        Returns:
            Normalized source (lowercase, no comments, minimal whitespace).
        """
        source_no_comments = helpers.remove_comments(source, file_ext)
        # Remove whitespaces except newlines
        source_compact = common.WHITESPACE_REGEX.sub("", source_no_comments)
        # Convert to lowercase
        return source_compact.lower()

    def _query_bloomfilter(self, source_norm_lines: str, magic_ext: int) -> None:
        """Query Bloom filter against source to find patch matches.

        Uses n-gram hashing and Bloom filters to efficiently detect matches.

        Args:
            source_norm_lines: Normalized source code.
            magic_ext: File extension type index.
        """
        tokens = source_norm_lines.split()

        for patch_id in range(0, self._npatch):
            if len(tokens) < common.ngram_size:
                common.verbose_print('Warning: source too short for n-gram analysis')
                return

            common.ngram_size = self._patch_list[patch_id][6]
            self._bit_vector.setall(0)
            num_ngram = len(tokens) - common.ngram_size + 1
            num_ngram_processed = 0

            # Build Bloom filter from n-grams
            for i in range(0, num_ngram):
                if num_ngram_processed > common.bloomfilter_size / common.min_mn_ratio:
                    # Reset and re-check against old hashes
                    self._check_bloom_match(patch_id)
                    num_ngram_processed = 0
                    self._bit_vector.setall(0)

                ngram = ''.join(tokens[i : i + common.ngram_size])
                hash1 = common.fnv1a_hash(ngram) & (common.bloomfilter_size - 1)
                hash2 = common.djb2_hash(ngram) & (common.bloomfilter_size - 1)
                hash3 = common.sdbm_hash(ngram) & (common.bloomfilter_size - 1)
                self._bit_vector[hash1] = 1
                self._bit_vector[hash2] = 1
                self._bit_vector[hash3] = 1
                num_ngram_processed += 1
                self._source_hashes.append([ngram, [hash1, hash2, hash3]])

            # Final check against patch hashes
            self._check_patch_hashes(patch_id)

    def _check_bloom_match(self, patch_id: int) -> None:
        """Check if old patch hashes match current Bloom filter.

        Args:
            patch_id: The patch identifier.
        """
        hash_list_old = self._patch_list[patch_id].get('old_norm_lines', [])
        is_match = True
        for h in hash_list_old:
            if not self._bit_vector[h]:
                is_match = False
                break
        if is_match:
            if patch_id not in self._match_dict:
                self._match_dict[patch_id] = []
            self._match_dict[patch_id].append(self._nsource)
            self._nmatch += 1

    def _check_patch_hashes(self, patch_id: int) -> None:
        """Check and record patch hash matches against Bloom filter.

        Args:
            patch_id: The patch identifier.
        """
        hash_list = self._patch_list[patch_id].hash_list
        i = 0
        seq = 0
        for h in hash_list:
            if i == 3:
                i = 0
                seq += 1

            if patch_id not in self._match_dict:
                self._match_dict[patch_id] = {}

            if seq not in self._match_dict[patch_id]:
                self._match_dict[patch_id][seq] = {}

            is_match = bool(self._bit_vector[h])
            self._results[h] = {'Match': is_match}
            self._match_dict[patch_id][seq][h] = is_match
            i += 1

    def items(self) -> List[Any]:
        """Return the source list."""
        return self._source_list

    def length(self) -> int:
        """Return the number of sources."""
        return self._nsource

    def match_items(self) -> Dict[int, Any]:
        """Return the match dictionary."""
        return self._match_dict

    def results(self) -> Dict[int, Dict[str, Any]]:
        """Return the results dictionary."""
        return self._results

    def source_hashes(self) -> List[Tuple[str, List[int]]]:
        """Return the source hashes list."""
        return self._source_hashes