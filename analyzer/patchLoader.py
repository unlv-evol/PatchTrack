"""Patch loader for analyzing patch files.

The PatchLoader class loads and processes patch files (unified diff format),
builds hash lists using n-grams, and tracks added/removed lines.
"""

import os
import re
import time
from typing import Dict, List, Tuple

from . import common
from . import helpers

# Magic number constants
MIN_FILE_EXT_TYPE = 2  # Minimum supported file extension type index
MAX_FILE_EXT_TYPE = 40  # Maximum supported file extension type index


class PatchLoader:
    """Loads and processes patch files using diff format and n-gram hashing."""

    def __init__(self) -> None:
        """Initialize the PatchLoader with empty data structures."""
        self._patch_list: List[common.PatchInfo] = []
        self._npatch: int = 0
        self._hashes: Dict[int, str] = {}
        self._only_removed: List[List[str]] = []
        self._only_added: List[List[str]] = []

    def traverse(self, patch_path: str, patch_type: str, file_ext: int) -> int:
        """Traverse patch files and process them.

        Args:
            patch_path: Path to a patch file or directory.
            patch_type: Type of patch ('buggy' or 'patch').
            file_ext: File extension type index.

        Returns:
            The number of patches processed.
        """
        start_time = time.time()

        if os.path.isfile(patch_path):
            common.verbose_print(f'  [-] {patch_path}: {file_ext}')
            if MIN_FILE_EXT_TYPE <= file_ext < MAX_FILE_EXT_TYPE:
                self._process_patch_file(patch_path, patch_type, file_ext)
        elif os.path.isdir(patch_path):
            for root, dirs, files in os.walk(patch_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    common.verbose_print(f'  [-] {file_path}: {file_ext}')
                    if MIN_FILE_EXT_TYPE <= file_ext < MAX_FILE_EXT_TYPE:
                        self._process_patch_file(file_path, patch_type, file_ext)
                        if patch_type == 'buggy':
                            self.important_hashes = []

        self._npatch = len(self._patch_list)
        elapsed_time = time.time() - start_time
        return self._npatch

    def _process_patch_file(self, patch_path: str, patch_type: str, file_type: int) -> None:
        """Route patch processing based on type.

        Args:
            patch_path: Path to the patch file.
            patch_type: 'buggy' or 'patch'.
            file_type: File extension type index.
        """
        if patch_type == 'buggy':
            self._process_buggy(patch_path, file_type)
        elif patch_type == 'patch':
            self._process_patch(patch_path, file_type)

    def _add_patch_from_diff(
        self,
        patch_filename: str,
        diff_file: str,
        diff_cnt: int,
        diff_lines: List[str],
        diff_orig_lines: List[str],
        file_type: int,
    ) -> None:
        """Add a patch record from diff hunks.

        Normalizes diff lines and builds hash list if sufficient length.

        Args:
            patch_filename: Name of the patch file.
            diff_file: Path to the file being diffed.
            diff_cnt: Diff hunk counter.
            diff_lines: Lines from the diff.
            diff_orig_lines: Original formatted lines for display.
            file_type: File extension type index.
        """
        diff_norm_lines = self._normalize(''.join(diff_lines), file_type).split()

        if len(diff_norm_lines) >= common.ngram_size:
            path = f'[{patch_filename}] {diff_file} #{diff_cnt}'
            hash_list, patch_hashes = self._build_hash_list(diff_norm_lines)
            self._patch_list.append(
                common.PatchInfo(
                    path, file_type, ''.join(diff_orig_lines),
                    diff_norm_lines, hash_list, patch_hashes, common.ngram_size
                )
            )
        else:
            # Adjust ngram_size if diff is too short
            common.ngram_size = len(diff_norm_lines)
            path = f'[{patch_filename}] {diff_file} #{diff_cnt}'
            hash_list, patch_hashes = self._build_hash_list(diff_norm_lines)
            self._patch_list.append(
                common.PatchInfo(
                    path, file_type, ''.join(diff_orig_lines),
                    diff_norm_lines, hash_list, patch_hashes, common.ngram_size
                )
            )

    def _process_buggy(self, patch_path: str, file_type: int) -> None:
        """Process a 'buggy' patch file (removed lines).

        Args:
            patch_path: Path to the patch file.
            file_type: File extension type index.
        """
        patch_filename = os.path.basename(patch_path)
        with open(patch_path, 'r') as f:
            patch_lines = f.readlines()

        diff_file = re.sub(r'\.patch$', '', patch_path)
        diff_cnt = 0
        diff_buggy_lines = []
        diff_orig_lines = []
        removed_lines = []

        for line in patch_lines:
            if line.startswith('@@'):
                if diff_buggy_lines:
                    self._add_patch_from_diff(
                        patch_filename, diff_file, diff_cnt,
                        diff_buggy_lines, diff_orig_lines, file_type
                    )
                    diff_buggy_lines.clear()
                    diff_orig_lines.clear()

                if removed_lines:
                    for removed in removed_lines:
                        removed_norm = self._normalize(removed, file_type).split()
                        self._only_removed.append(removed_norm)
                    removed_lines.clear()

                diff_cnt += 1

            elif line.startswith('-'):
                diff_buggy_lines.append(line[1:])
                diff_orig_lines.append('<font color="#AA0000">')
                diff_orig_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                diff_orig_lines.append('</font>')
                removed_lines.append(line[1:])

            elif line.startswith(' '):
                diff_buggy_lines.append(line[1:])
                diff_orig_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))

        # Process final diff hunk if any
        if diff_buggy_lines:
            self._add_patch_from_diff(
                patch_filename, diff_file, diff_cnt,
                diff_buggy_lines, diff_orig_lines, file_type
            )

            if removed_lines:
                for removed in removed_lines:
                    removed_norm = self._normalize(removed, file_type).split()
                    self._only_removed.append(removed_norm)

    def _process_patch(self, patch_path: str, file_type: int) -> None:
        """Process a 'patch' file (added lines).

        Args:
            patch_path: Path to the patch file.
            file_type: File extension type index.
        """
        patch_filename = os.path.basename(patch_path)
        with open(patch_path, 'r') as f:
            patch_lines = f.readlines()

        diff_file = re.sub(r'\.patch$', '', patch_path)
        diff_cnt = 0
        diff_patch_lines = []
        diff_orig_lines = []
        added_lines = []

        for line in patch_lines:
            if line.startswith('@@'):
                if diff_patch_lines:
                    self._add_patch_from_diff(
                        patch_filename, diff_file, diff_cnt,
                        diff_patch_lines, diff_orig_lines, file_type
                    )
                    diff_patch_lines.clear()
                    diff_orig_lines.clear()

                if added_lines:
                    for added in added_lines:
                        added_norm = self._normalize(added, file_type).split()
                        self._only_added.append(added_norm)
                    added_lines.clear()

                diff_cnt += 1

            elif line.startswith('+'):
                diff_patch_lines.append(line[1:])
                diff_orig_lines.append('<font color="#00AA00">')
                diff_orig_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                diff_orig_lines.append('</font>')
                added_lines.append(line[1:])

            elif line.startswith(' '):
                diff_patch_lines.append(line[1:])
                diff_orig_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))

        # Process final diff hunk if any
        if diff_patch_lines:
            self._add_patch_from_diff(
                patch_filename, diff_file, diff_cnt,
                diff_patch_lines, diff_orig_lines, file_type
            )

            if added_lines:
                for added in added_lines:
                    added_norm = self._normalize(added, file_type).split()
                    self._only_added.append(added_norm)

    def _normalize(self, patch: str, file_ext: int) -> str:
        """Normalize patch content by removing comments and collapsing whitespace.

        Args:
            patch: Raw patch text.
            file_ext: File extension type index.

        Returns:
            Normalized patch text (lowercased, whitespace-collapsed).
        """
        source = patch.lower()
        source = helpers.remove_comment(source, file_ext)
        source = re.sub(common.WHITESPACE_REGEX, ' ', source).strip()
        return source

    def _build_hash_list(self, diff_norm_lines: List[str]) -> Tuple[List[int], List[Tuple[str, List[int]]]]:
        """Build n-gram hash list from normalized diff lines.

        Args:
            diff_norm_lines: Normalized lines split by whitespace.

        Returns:
            Tuple of (hash_list, patch_hashes) where hash_list contains hashes
            and patch_hashes contains (original_ngram, hash_list) tuples.
        """
        hash_list = []
        patch_hashes = []

        for i in range(len(diff_norm_lines) - common.ngram_size + 1):
            ngram = ' '.join(diff_norm_lines[i:i + common.ngram_size])
            fnv1a = common.fnv1a_hash(ngram)
            djb2 = common.djb2_hash(ngram)
            sdbm = common.sdbm_hash(ngram)

            hash_list.append(fnv1a)
            hash_list.append(djb2)
            hash_list.append(sdbm)
            patch_hashes.append((ngram, [fnv1a, djb2, sdbm]))

            self._hashes[fnv1a] = ngram
            self._hashes[djb2] = ngram
            self._hashes[sdbm] = ngram

        return hash_list, patch_hashes

    def items(self) -> List[common.PatchInfo]:
        """Get all patch items."""
        return self._patch_list

    def length(self) -> int:
        """Get number of patches loaded."""
        return len(self._patch_list)

    def hashes(self) -> Dict[int, str]:
        """Get mapping of hash to ngram."""
        return self._hashes

    def added(self) -> List[List[str]]:
        """Get all added lines."""
        return self._only_added

    def removed(self) -> List[List[str]]:
        """Get all removed lines."""
        return self._only_removed