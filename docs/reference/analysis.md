# Analysis Module

## Overview

The **Analysis** module provides visualization and plotting functions for PatchTrack classification results. It generates charts and graphs to help understand patch application patterns across pull requests and repositories.

### Purpose

This module:

- **Visualizes** classification distributions (PA, PN, NE, CC, ERROR)
- **Generates** bar charts, pie charts, and other plots
- **Creates** statistical summaries
- **Exports** results for reporting and publication

### Chart Types

| Chart Type | Purpose | Best For |
|-----------|---------|----------|
| **Bar Chart** | Absolute counts by classification | Overall distribution |
| **Pie Chart** | Percentage breakdown | Proportional understanding |
| **Line Chart** | Trends over repositories | Time-series analysis |
| **Heatmap** | 2D distribution | Multiple dimensions |

---

## Key Visualizations

### Classification Distribution
Shows how many patches fall into each category:
```
PA (Patch Applied)     ████████████ 45%
PN (Not Applied)       ██████ 25%
NE (Not Existing)      ███ 15%
CC (Cannot Classify)   ██ 10%
ERROR                  █ 5%
```

### Repository Comparison
Compares classification patterns across different repositories:

- X-axis: Repository name
- Y-axis: Count or percentage
- Groups: Classification type

### Trend Analysis
Tracks how patch application rates change:

- Over time
- Across project size ranges
- By programming language

---

## Usage Example

```python
from analyzer import analysis

# Basic bar chart of classification totals
totals_list = [45, 25, 15, 10, 5]  # PA, PN, NE, CC, ERROR
analysis.all_class_bar(totals_list, is_percentage=False)

# As percentage
analysis.all_class_bar(totals_list, is_percentage=True)

# Pie chart
analysis.all_class_pie(totals_list)

# Repository comparison
repo_data = {
    'repo1': [30, 20, 10, 5, 2],
    'repo2': [15, 5, 5, 5, 3],
}
analysis.repo_comparison_bar(repo_data)
```

---

## Output Formats

### Display

- **Interactive plots** in Jupyter notebooks
- **Static images** saved to disk
- **Console output** for quick analysis

### File Exports

- PNG images for publications
- CSV data for further analysis
- JSON for programmatic access

---

## Statistical Metrics

The module can calculate:

### Descriptive Statistics
- Mean, median, standard deviation
- Min/max values
- Quartile ranges

### Comparative Metrics
- Patch application rate
- Classification accuracy
- Inter-rater agreement (if multiple classifiers)

### Aggregation Levels
- Per repository
- Per programming language
- Per project size
- Overall

---

## Configuration

Common parameters:

```python
# Chart styling
figsize = (10, 6)           # Figure dimensions
dpi = 300                    # Resolution for exports
style = 'seaborn'            # Matplotlib style
colormap = 'viridis'         # Color scheme

# Data options
normalize = False            # Percentage vs absolute
log_scale = False            # Linear vs log scale
sort_by = 'value'            # Sort order
```

---

## API Reference

::: analyzer.analysis
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

---

## Integration Points

The analysis module is typically called:

1. **From `main.py`**: After classification completes
2. **From notebooks**: For exploratory analysis
3. **In CI/CD pipelines**: For automated reporting
4. **Standalone**: For custom analysis scripts

### Example Pipeline
```python
from analyzer import main, analysis

# Run classification
pt = main.PatchTrack(tokens)
pt.classify(pr_pairs)

# Get results
results = pt.get_results()
classifications = pt.pr_classifications

# Visualize
analysis.visualize_results(classifications)
```

---

## Output Examples

### Bar Chart Output
```
Classification Distribution
┌─────────────────────────────┐
│ PA  ████████████ 45 (45%)   │
│ PN  ██████ 25 (25%)         │
│ NE  ███ 15 (15%)            │
│ CC  ██ 10 (10%)             │
│ ERR █ 5 (5%)                │
└─────────────────────────────┘
```

---

## Tips & Best Practices

✅ **Do**

- Use descriptive titles for charts
- Include legends and axis labels
- Export with high DPI for publication
- Validate data before visualization

❌ **Don't**

- Exceed 5-6 categories in one chart
- Use 3D charts (hard to read)
- Mix different metrics in one chart
- Forget to add axis units

---

::: analyzer.analysis
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

## See Also

- [Aggregator](aggregator.md) - Produces data for visualization
- [Main](main.md) - Calls analysis after classification