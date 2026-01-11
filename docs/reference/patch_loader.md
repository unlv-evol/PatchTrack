# Patch Loader

## Overview

The `PatchLoader` class loads and processes patch files in unified diff format,
extracts added/removed lines, builds n-gram hash lists, and tracks patches by
file type. It is a core component of the PatchTrack pipeline responsible for
normalizing and preparing patch data for classification.

This page explains the workflow, key methods, data structures, and tuning
parameters. For the complete API reference and docstrings, see the
mkdocstrings section below.

## Purpose

- Load patch files from the filesystem (single files or directory trees)
- Extract added lines (from patch files) and removed lines (from buggy files)
- Normalize content by removing comments and collapsing whitespace
- Build n-gram hash lists using three independent hash functions
- Track file type information for language-aware processing

## Key Concepts

### Patch Types

- **Buggy patches**: Files with removed lines (prefixed with `-` in diff format)
  represent the original buggy code
- **Patch files**: Files with added lines (prefixed with `+` in diff format)
  represent the fix/patch applied to address the bug

### N-gram hashing

Sequences of `NGRAM_SIZE` tokens are hashed using three hash functions:

- **FNV-1a**: Fast, non-cryptographic hash
- **DJB2**: Daniel J. Bernstein's hash
- **SDBM**: SDBM hash function

All three hashes are stored for each n-gram to improve matching robustness
(three independent hash functions reduce collision risk).

### Normalization

Raw patch lines are normalized by:

1. Converting to lowercase
2. Removing language-specific comments (using `helpers.remove_comment()`)
3. Collapsing whitespace and splitting into tokens

### File Type Index

The `file_ext` parameter is an integer index (2–39 range) that identifies
the file type/language. This is used to apply language-specific comment removal
and tokenization rules. The index maps to extensions defined in
`analyzer.constant.EXTENSIONS`.

## Workflow

```
PatchLoader.traverse(patch_path, patch_type, file_ext)
    │
    ├─── For each patch file:
    │
    ├─── _process_patch_file() routes to:
    │    ├─ _process_buggy()  [removed lines]
    │    └─ _process_patch()  [added lines]
    │
    ├─── For each diff hunk (@@):
    │    ├─ Extract lines (- or +)
    │    ├─ Format for display (HTML color tags)
    │    └─ Call _add_patch_from_diff()
    │
    ├─── _add_patch_from_diff():
    │    ├─ Normalize lines
    │    ├─ Call _build_hash_list()
    │    ├─ Create PatchInfo object
    │    └─ Append to _patch_list
    │
    └─── Return count of patches loaded
```

## Key Methods

| Method | Returns | Purpose |
|---|---|---|
| `traverse(patch_path, patch_type, file_ext)` | `int` | Load and process all patches from path; return count. Routes to `_process_buggy()` or `_process_patch()`. |
| `_process_buggy(patch_path, file_ext)` | `None` | Extract removed lines (prefix `-`), accumulate diff hunks, and call `_add_patch_from_diff()`. |
| `_process_patch(patch_path, file_ext)` | `None` | Extract added lines (prefix `+`), accumulate diff hunks, and call `_add_patch_from_diff()`. |
| `_add_patch_from_diff(...)` | `None` | Normalize diff lines, build hash list, create `PatchInfo`, append to internal list. |
| `_normalize(patch, file_ext)` | `str` | Remove comments, collapse whitespace, lowercase. |
| `_build_hash_list(diff_norm_lines)` | `Tuple` | Compute FNV-1a, DJB2, SDBM hashes for each n-gram. Return `(hash_list, patch_hashes)`. |
| `items()` | `List[PatchInfo]` | Get all loaded `PatchInfo` objects. |
| `length()` | `int` | Get count of loaded patches. |
| `hashes()` | `Dict[int, str]` | Get hash-to-ngram lookup table. |
| `added()` | `List[List[str]]` | Get all added (patch) lines as token lists. |
| `removed()` | `List[List[str]]` | Get all removed (buggy) lines as token lists. |

## Data Structures

### `PatchInfo` (from `common.py`)

Each patch record contains:

```python
PatchInfo(
    path: str,                      # "[filename] file.py #2" (patch id)
    file_type: int,                 # File extension type index (2-39)
    diff_orig_lines: str,           # Raw diff lines (HTML-formatted)
    diff_norm_lines: List[str],     # Normalized tokens
    hash_list: List[int],           # All hashes (fnv1a, djb2, sdbm per n-gram)
    patch_hashes: List[Tuple[...]], # (ngram_str, [hash1, hash2, hash3])
    ngram_size: int                 # Size of n-grams used
)
```

### Hash Storage

Internal `_hashes: Dict[int, str]` maps hash values to n-gram strings for
reverse lookup. Built and populated during `_build_hash_list()`.

## Usage Example

### Basic usage (CLI-like)

```python
from analyzer.patchLoader import PatchLoader

loader = PatchLoader()

# Process buggy patches (removed lines)
buggy_count = loader.traverse(
    patch_path='data/buggy/',
    patch_type='buggy',
    file_ext=2  # Language type index for Python
)
print(f"Loaded {buggy_count} buggy patches")

# Process fixes (added lines)
patch_count = loader.traverse(
    patch_path='data/patches/',
    patch_type='patch',
    file_ext=2
)
print(f"Loaded {patch_count} patch files")

# Inspect results
for patch_info in loader.items():
    print(f"Patch: {patch_info.path}")
    print(f"  File type: {patch_info.file_type}")
    print(f"  Hashes: {len(patch_info.hash_list)}")
    print(f"  N-gram size: {patch_info.ngram_size}")

# Retrieve specific data
hash_map = loader.hashes()  # Dict[hash_value] -> ngram string
removed_lines = loader.removed()  # List of removed token lists
added_lines = loader.added()  # List of added token lists
```

### Processing a single file

```python
loader = PatchLoader()
loader.traverse(
    patch_path='data/buggy/file.patch',
    patch_type='buggy',
    file_ext=2
)
```

## N-gram Size and Performance

- Default `NGRAM_SIZE` from `analyzer.constant` is `1`.
- Larger n-grams (e.g., 3–7) reduce false positives but increase hashing
  overhead and may decrease recall.
- If a diff is shorter than `ngram_size`, the `ngram_size` is reduced
  dynamically in `_add_patch_from_diff()` to match the diff length.
- The `ngram_size` used is stored in each `PatchInfo` for later reference.

## Best Practices

- Use consistent `file_ext` indices across buggy and patch processing to
  ensure language-aware normalization is applied uniformly.
- Pre-validate patch file format (unified diff) before passing to
  `traverse()`.
- Monitor `_npatch` or call `length()` to confirm patches were loaded
  successfully.
- Store `loader.hashes()` for reverse-lookup if you need to map hash values
  back to n-gram strings during classification.

## Notes on Comments Removal

The `_normalize()` method calls `helpers.remove_comment(source, file_ext)` to
strip language-specific comments before tokenization. The `file_ext` parameter
tells the helper which language syntax to use (e.g., `#` for Python, `//` for
Java, etc.). See `docs/reference/helpers.md` for details.

## API Reference

::: analyzer.patchLoader
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source


## See Also

- [Main Module](main.md) — How patches are loaded in the pipeline
- [Classifier](classifier.md) — How hash lists are used for matching
- [Constant](constant.md) — File type indices and `NGRAM_SIZE`
- [Helpers](helpers.md) — Comment removal for different languages