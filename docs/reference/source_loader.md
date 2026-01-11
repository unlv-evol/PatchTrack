# Source Loader

## Overview

The `SourceLoader` class traverses source files in a repository, normalizes them
(removes comments, collapses whitespace), and uses Bloom filters to efficiently
detect matches against known patches. It is a critical component of the
PatchTrack pipeline for identifying where patches may have been applied in
source code.

This page explains the workflow, Bloom filter approach, key methods, data
structures, and matching logic. For the complete API reference and docstrings,
see the mkdocstrings section below.

## Purpose

- Load and traverse source files from the filesystem (single files or trees)
- Normalize source code by removing language-specific comments
- Build Bloom filters for fast probabilistic n-gram matching
- Detect patches in source files using hash-based queries
- Record matches and provide detailed results

## Key Concepts

### Bloom Filters

A Bloom filter is a space-efficient probabilistic data structure used to test
whether an element is a member of a set. In SourceLoader:

- A bit vector of size `BLOOMFILTER_SIZE` (2,097,152 bits ≈ 256 KB) stores
  presence information
- Each n-gram is hashed three ways (FNV-1a, DJB2, SDBM) to set 3 bits
- A query checks if all 3 hash bits are set; if not, the element is definitely
  not in the set
- **Trade-off**: False positives possible, false negatives impossible

### Normalization

Source code is normalized by:

1. Removing language-specific comments (using `helpers.remove_comments()`)
2. Collapsing whitespace (all whitespace replaced with empty string)
3. Converting to lowercase
4. Splitting into tokens

This aggressive normalization ensures consistent matching regardless of
formatting or comments.

### Matching Strategy

- Source code is split into sliding n-grams
- Each source n-gram is hashed and stored in the Bloom filter
- For each patch, all patch hashes are queried against the Bloom filter
- Matches are recorded with patch ID and position information

### Batch Processing

To avoid memory overflow with very large source files:

- Bloom filter is rebuilt periodically (when `num_ngram_processed` exceeds
  `BLOOMFILTER_SIZE / MIN_MN_RATIO`)
- Old patch hashes are checked against the current filter before reset
- This creates "batches" of hashes within the file

## Workflow

```
SourceLoader.traverse(source_path, patch, file_ext)
    │
    ├─── Store patch_list and count from patch object
    │
    ├─── For each source file:
    │
    ├─── _process(source_path, file_ext):
    │    ├─ Read file
    │    ├─ Call _normalize()
    │    └─ Call _query_bloomfilter()
    │
    ├─── _query_bloomfilter():
    │    ├─ Split source into tokens
    │    │
    │    ├─ For each patch:
    │    │  │
    │    │  ├─ Build Bloom filter from source n-grams
    │    │  ├─ For each batch:
    │    │  │  ├─ _check_bloom_match() [against old hashes]
    │    │  │  └─ Reset Bloom filter
    │    │  │
    │    │  └─ _check_patch_hashes() [final check]
    │    │
    │    └─ Record matches in _match_dict
    │
    └─── Return total match count
```

## Key Methods

| Method | Returns | Purpose |
|---|---|---|
| `traverse(source_path, patch, file_ext)` | `int` | Load and analyze source files; query against patches. Return total matches. |
| `_process(source_path, magic_ext)` | `None` | Read a source file and normalize it; call `_query_bloomfilter()`. |
| `_normalize(source, file_ext)` | `str` | Remove comments, collapse whitespace, lowercase. Return normalized string. |
| `_query_bloomfilter(source_norm_lines, magic_ext)` | `None` | Build Bloom filter from source n-grams and query against all patches. Handles batch processing and resets. |
| `_check_bloom_match(patch_id)` | `None` | Query old patch hashes against current Bloom filter; record matches. |
| `_check_patch_hashes(patch_id)` | `None` | Check all hashes from current patch against Bloom filter; populate `_match_dict` and `_results`. |
| `items()` | `List` | Get source file list. |
| `length()` | `int` | Get count of source files processed. |
| `match_items()` | `Dict` | Get match dictionary mapping patch ID → matches. |
| `results()` | `Dict` | Get results dictionary with per-hash match status. |
| `source_hashes()` | `List[Tuple]` | Get source n-gram hashes `[(ngram_str, [hash1, hash2, hash3]), ...]`. |

## Data Structures

### Match Dictionary

`_match_dict: Dict[int, Dict[int, Dict[int, bool]]]` maps:

```python
{
    patch_id: {
        seq_num: {
            hash_value: is_match_bool,
            ...
        },
        ...
    },
    ...
}
```

Where:
- `patch_id`: Identifier from patch list
- `seq_num`: Sequence number of n-gram within patch (increments every 3 hashes)
- `hash_value`: One of the three hash values (FNV-1a, DJB2, SDBM)
- `is_match_bool`: Whether this hash was found in Bloom filter

### Results Dictionary

`_results: Dict[int, Dict[str, Any]]` maps hash values to match results:

```python
{
    hash_value: {'Match': is_match_bool},
    ...
}
```

### Source Hashes List

`_source_hashes: List[Tuple[str, List[int]]]` stores n-grams and their hashes:

```python
[
    (ngram_str, [fnv1a, djb2, sdbm]),
    (ngram_str, [fnv1a, djb2, sdbm]),
    ...
]
```

## Usage Example

### Basic workflow

```python
from analyzer.patchLoader import PatchLoader
from analyzer.sourceLoader import SourceLoader

# Load patches first
loader = PatchLoader()
loader.traverse('data/buggy/', patch_type='buggy', file_ext=2)

# Now query source against patches
source_loader = SourceLoader()
match_count = source_loader.traverse(
    source_path='data/src/',
    patch=loader,
    file_ext=2  # Same file type index
)
print(f"Found {match_count} possible matches")

# Inspect results
matches = source_loader.match_items()
for patch_id, match_info in matches.items():
    print(f"Patch {patch_id}: {match_info}")
```

### Checking specific hashes

```python
source_loader = SourceLoader()
source_loader.traverse('data/src/', loader, file_ext=2)

results = source_loader.results()
for hash_val, result in results.items():
    if result['Match']:
        print(f"Hash {hash_val} found in source")

# Reverse lookup
source_ngrams = source_loader.source_hashes()
for ngram, hashes in source_ngrams:
    print(f"N-gram: {ngram} -> Hashes: {hashes}")
```

## Bloom Filter Tuning

### Memory and False Positive Trade-offs

- `BLOOMFILTER_SIZE` (default 2,097,152): Larger size = fewer false positives
  but more memory used.
- `MIN_MN_RATIO` (default 32): Controls batch boundary. Smaller ratio = more
  frequent resets and checks, reducing false positives but increasing
  computation.

### Batch Size Calculation

When `num_ngram_processed` exceeds `BLOOMFILTER_SIZE / MIN_MN_RATIO`:

```
Batch size threshold = 2,097,152 / 32 ≈ 65,536 n-grams per batch
```

For typical file with 10 KB of normalized tokens, this means ~100+ batches.
Adjust `MIN_MN_RATIO` or `BLOOMFILTER_SIZE` to tune performance vs. accuracy.

## Best Practices

- Use consistent `file_ext` indices across both `PatchLoader` and
  `SourceLoader` to ensure language-aware normalization is uniform.
- Verify source files are readable (handle encoding errors gracefully).
- Consider pre-filtering source files by size (skip very large files if
  memory-constrained).
- Store `match_items()` and `results()` for post-processing and analysis.
- Use `source_hashes()` for debugging mismatches or reverse n-gram lookup.

## Notes on Bloom Filter Implementation

The code uses `bitarray.bitarray` from the `bitarray` package for efficient
bit manipulation. The Bloom filter is reset between batches to manage memory
usage on large files. This means the final `_check_patch_hashes()` checks
only the last batch; earlier batches are checked via `_check_bloom_match()`
during the resets.

## Integration with PatchLoader and Classifier

- **Input**: `PatchLoader` provides normalized patches and their hash lists
- **Output**: Match information passed to `classifier` for further analysis
- **See**: `docs/reference/classifier.md` for how matches are scored and
  classified as PA/PN/NE

## API Reference

::: analyzer.sourceLoader
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

## See Also

- [Main Module](main.md) — How source loading fits in the pipeline
- [Patch Loader](patch_loader.md) — How patches are prepared
- [Classifier](classifier.md) — How matches are classified
- [Constant](constant.py) — `BLOOMFILTER_SIZE` and `MIN_MN_RATIO`
- [Helpers](helpers.md) — Comment removal for different languages