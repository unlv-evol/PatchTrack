# Classifier Module

## Overview

The **Classifier** module provides core patch classification functions used by PatchTrack's pipeline. It determines whether a ChatGPT code snippet matches patches in a GitHub pull request by comparing hunks, calculating similarities, and aggregating results into classification decisions.

### Purpose

This module:

- **Processes** patches and source code with tokenization
- **Matches** code hunks using hash-based comparison
- **Calculates** similarity ratios between snippets
- **Classifies** individual patches as PA, PN, or NE
- **Preserves** original logic with improved readability

### Classification Algorithm

```
ChatGPT Code + PR Patch
         ↓
   Tokenize Both
         ↓
   Create Hash Tables
         ↓
   Find Matching Hunks
         ↓
   Calculate Similarity Ratio
         ↓
   Classify Based on Matches
         ↓
    PA / PN / NE
```

---

## Key Concepts

### Hunks
A "hunk" is a continuous block of added code in the patch. The classifier matches hunks from ChatGPT code against PR patches.

### Hash-Based Matching
Uses `sha256` hashes to compare:

- **Source hashes**: Hash values of each line in ChatGPT code
- **Patch hunks**: Added code blocks in PR patches
- **Match**: When hashes align between source and patch

### Similarity Ratio
Calculated using n-gram comparison:

- **Range**: 0.0 (no match) to 1.0 (perfect match)
- **Formula**: Matching n-grams / Total n-grams
- **Usage**: Determines confidence in classification

---

## Classification Decision

### Patch Applied (PA)
✅ Conditions:

- ChatGPT code appears in one or more PR hunks
- High similarity ratio to patch content
- Hashes match between source and patch

### Patch Not Applied (PN)
❌ Conditions:

- ChatGPT code does NOT appear in any PR hunk
- No matching hashes found
- Similarity ratio is low

### Not Existing (NE)
⚠️ Conditions:

- Required file doesn't exist in PR
- ChatGPT code path cannot be processed

---

## Key Functions

### Core Processing

- **`process_patch()`**: Load and traverse patch file with source code
- **`get_ext()`**: Extract file extension from filename

### Matching Functions

- **`find_hunk_matches()`**: Find hash-based matches between hunks
- **`find_hunk_matches_w_important_hash()`**: Enhanced matching with priority hashes
- **`calculate_match_percentage()`**: Calculate proportion of matched items

### Classification Functions

- **`classify_hunk()`**: Classify a single hunk
- **`classify_patch()`**: Aggregate hunk classifications to patch level
- **`cal_similarity_ratio()`**: Calculate n-gram based similarity

---

## Usage Example

```python
from analyzer import classifier, common

# Set n-gram size (global setting)
common.ngram_size = 4

# Process a patch and source
patch_loader, source_loader = classifier.process_patch(
    patch_path='data/patches/pr-123/github/patch-1.patch',
    dst_path='data/patches/pr-123/chatgpt/code.py',
    type_patch='patch',
    file_ext=5
)

# Extract components
added_code = patch_loader.added()
match_items = source_loader.match_items()
source_hashes = source_loader.source_hashes()

# Find matches with important hashes
hunk_matches = classifier.find_hunk_matches_w_important_hash(
    match_items=match_items,
    _type='PA',
    important_hashes=added_code,
    source_hashes=source_hashes
)

# Calculate similarity
similarity = classifier.cal_similarity_ratio(source_hashes, added_code)
print(f"Similarity Ratio: {similarity:.2%}")

# Classify hunks
hunk_classes = []
for hunk_id in hunk_matches:
    hunk_class = classifier.classify_hunk('', hunk_matches[hunk_id]['class'])
    hunk_classes.append(hunk_class)

# Final patch classification
final_class = classifier.classify_patch(hunk_classes)
print(f"Patch Classification: {final_class}")
```

---

## Data Structures

### Patch Loader Output
```python
{
    'hunks': [
        {'added': [...], 'removed': [...], 'context': [...]},
        ...
    ],
    'hashes': {hash_value: {'count': n, 'lines': [...]}, ...}
}
```

### Source Loader Output
```python
{
    'tokens': [...],
    'hashes': {hash_value: position, ...},
    'match_items': {hash: {'Match': True/False}, ...}
}
```

### Match Results
```python
{
    'hunk_0': {
        'class': 'PA',
        'matches': 25,
        'total': 30,
        'percentage': 83.33
    }
}
```

---

## Performance Considerations

- **Hash-based**: O(n) complexity for matching
- **N-gram size**: Trade-off between accuracy and speed
  - Small n (1-2): Faster, fewer matches
  - Large n (4+): Slower, more accurate
- **File size**: Larger files take longer to process

---

## API Reference

::: analyzer.classifier
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

---

## See also

- [Patch Loader](patch_loader.md) - Parses PR patches
- [Source Loader](source_loader.md) - Parses ChatGPT code
- [Aggregator](aggregator.md) - Aggregates classifications
- [Common](common.md) - Configuration (n-gram size, etc.)