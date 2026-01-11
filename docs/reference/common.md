# Common Module

## Overview

The **Common** module provides shared configuration and global settings used throughout PatchTrack. It manages state variables and utilities needed across multiple modules.

### Purpose

This module:
- **Stores** global configuration variables
- **Manages** n-gram size settings
- **Provides** common utility constants
- **Enables** cross-module communication

---

## Key Configuration Variables

### N-gram Size
Controls the granularity of code comparison:

```python
import analyzer.common as common

# Set n-gram size (lines of code per token)
common.ngram_size = 1    # Default: compare line-by-line
common.ngram_size = 2    # Compare pairs of lines
common.ngram_size = 4    # Compare 4-line blocks
```

**Impact on Classification:**
| N-gram Size | Speed | Precision | Use Case |
|-----------|-------|-----------|----------|
| 1 | Fast | Low | Quick scans |
| 2-3 | Medium | Medium | Standard |
| 4+ | Slow | High | Detailed analysis |

!!! tip "Recommended"
    Use n-gram size of **2-4** for most analysis. Larger values may miss partial matches.

---

## Usage Patterns

### Setting Global State
```python
from analyzer import common, classifier

# Configure before classification
common.ngram_size = 4

# Run classification with this setting
patch_loader, source_loader = classifier.process_patch(...)
```

### Multiple Classifications with Different Settings
```python
from analyzer import common, main

# First run: n-gram size 2
common.ngram_size = 2
pt1 = main.PatchTrack(tokens)
pt1.classify(pr_pairs)

# Second run: n-gram size 4
common.ngram_size = 4
pt2 = main.PatchTrack(tokens)
pt2.classify(pr_pairs)

# Compare results
compare(pt1.pr_classifications, pt2.pr_classifications)
```

---

## Configuration Impact

### How N-gram Size Affects Results

**Low N-gram Size (1-2):**
- ✅ Fast processing
- ✅ Catches small code snippets
- ❌ More false positives
- ❌ May match unrelated code

**High N-gram Size (4+):**
- ✅ Fewer false positives
- ✅ More precise matches
- ❌ Slower processing
- ❌ Misses small changes

### Example
```
ChatGPT Code:
    x = 5
    y = 10
    z = x + y

N-gram Size 1: [x, y, z, 5, 10]
N-gram Size 2: [(x,5), (y,10), (z,x+y)]
N-gram Size 4: [(x,5,y,10), (y,10,z,x+y)]
```

---

## Best Practices

✅ **Do**
- Set n-gram size once at initialization
- Use consistent settings for all PRs in a batch
- Document your choice in results metadata
- Experiment to find optimal value for your data

❌ **Don't**
- Change n-gram size during classification
- Use values below 1 or above 10
- Assume one setting works for all cases
- Forget to reset settings between runs

---

## Typical Configuration Values

### For Different Project Types

| Project Type | Recommended | Reason |
|-------------|-------------|--------|
| Small snippets | 1-2 | Capture brief code changes |
| Regular code | 2-3 | Balanced accuracy/speed |
| Complex logic | 4-5 | Need more context |
| Large methods | 5+ | Comprehensive matching |

---

## Integration with Other Modules

The common module is used by:

- **classifier.py**: Sets n-gram size via `common.ngram_size`
- **patchLoader.py**: Respects current n-gram setting
- **sourceLoader.py**: Uses n-gram configuration
- **main.py**: May set configuration before processing

```
main.py
  ↓
  └── common.ngram_size = value
       ↓
       ├── classifier.py
       ├── patchLoader.py
       └── sourceLoader.py
```

---

## API Reference

::: analyzer.common
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

---

## Configuration Checklist

Before running classification:

- [ ] Import common module
- [ ] Set appropriate n-gram size
- [ ] Verify setting with print statement
- [ ] Run classification
- [ ] Document configuration in results
- [ ] Reset if running multiple analyses

---

## Related Modules

- [Classifier](classifier.md) - Uses n-gram configuration
- [Patch Loader](patch_loader.md) - Tokenizes based on n-grams
- [Source Loader](source_loader.md) - Processes code with n-grams
- [Main](main.md) - May initialize configuration