# Aggregator Module

## Overview

The **Aggregator** module is responsible for converting per-file patch classifications into PR-level final decisions. It aggregates individual file classification results and produces summary statistics across all patches in a pull request.

### Purpose

After classifying individual patches against ChatGPT code snippets, this module:
- **Aggregates** file-level classifications to PR-level decisions
- **Counts** classification distribution (PA, PN, NE, CC, ERROR)
- **Determines** final PR status based on heuristics
- **Persists** results to disk for analysis

### Classification Hierarchy

```
Per-File Classification (from classifier.py)
         ↓
    PA, PN, NE, CC, ERROR
         ↓
    Aggregator (this module)
         ↓
PR-Level Classification (final decision)
```

---

## Key Functions

### Final Classification Determination
The module uses the following logic to determine PR-level classification:

- **PA (Patch Applied)**: If any file is classified as PA
- **PN (Patch Not Applied)**: If all files are PN
- **NE (Not Existing)**: If all files are NE or missing
- **CC (Cannot Classify)**: If mixed results prevent clear decision
- **ERROR**: If processing errors occurred

### Usage Example

```python
from analyzer import aggregator

# Aggregate file-level classifications into PR decisions
pr_results = {
    'PR-123': {
        'file1.py': {'result': [{'patchClass': 'PA'}, {'patchClass': 'PN'}]},
        'file2.py': {'result': [{'patchClass': 'PA'}]}
    }
}

# Get final classification per PR
final_classes = aggregator.final_class(pr_results)
# Output: {'PR-123': {'class': 'PA', 'files': 2, ...}}

# Get statistics
stats = aggregator.count_all_classifications(final_classes)
# Output: {'PA': 1, 'PN': 0, 'NE': 0, 'CC': 0, 'ERROR': 0}
```

---

## Classification Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `CLASS_PATCH_APPLIED` | `PA` | Patch was successfully applied |
| `CLASS_PATCH_NOT_APPLIED` | `PN` | Patch was not applied |
| `CLASS_NOT_EXISTING` | `NE` | File doesn't exist in PR |
| `CLASS_CANNOT_CLASSIFY` | `CC` | Unable to classify |
| `CLASS_ERROR` | `ERROR` | Processing error occurred |
| `CLASS_OTHER_EXT` | `OTHER EXT` | Unsupported file extension |

---

## Data Structures

### Input Format
Per-file classification results from classifier:
```python
{
    'PR-123': {
        'file1.py': {
            'result': [
                {
                    'patchClass': 'PA',
                    'similarityRatio': 0.95,
                    'hunkMatches': {...},
                    'PrLink': 'https://github.com/...'
                },
                ...
            ]
        }
    }
}
```

### Output Format
PR-level aggregated results:
```python
{
    'PR-123': {
        'class': 'PA',
        'count': 2,
        'files': ['file1.py', 'file2.py'],
        'pa_count': 1,
        'pn_count': 1,
        'ne_count': 0,
        'cc_count': 0,
        'error_count': 0
    }
}
```

---

## API Reference

::: analyzer.aggregator
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

---

## Related Modules

- [Classifier](classifier.md) - Classifies individual patches
- [Main](main.md) - Orchestrates the analysis pipeline
- [Analysis](analysis.md) - Visualizes aggregated results