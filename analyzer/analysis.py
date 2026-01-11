"""Visualization module for PatchTrack analysis.

Provides functions to generate bar charts, pie charts, and grouped visualizations
for analyzing patch classification patterns and integration metrics.
"""

from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Color palette for consistent visualization
COLOR_PATCH_APPLIED = "#377eb8"
COLOR_CANNOT_CLASSIFY = "#984ea3"
COLOR_NOT_EXISTING = "#ff7f00"
COLOR_PATCH_NOT_APPLIED = "#e41a1c"
COLOR_ERROR = "#a65628"
COLOR_MISSED_OPPORTUNITY = "#e41a1c"
COLOR_EFFORT_DUPLICATION = "#377eb8"
COLOR_SPLIT = "#4daf4a"
COLOR_ADDED_FILE = "#F5D9E7"
COLOR_DELETED_FILE = "#7FC0D0"
COLOR_UNINTERESTING = "#a65628"
COLOR_EVEN_DISTRIBUTION = "#FF1493"
COLOR_NOT_APPLICABLE = "#ffff33"

# Classification labels
LABEL_PATCH_APPLIED = "Patch Applied"
LABEL_CANNOT_CLASSIFY = "Cannot Classify"
LABEL_NOT_EXISTING = "Not Existing Patch"
LABEL_PATCH_NOT_APPLIED = "Patch Not Applied"
LABEL_ERROR = "Error"
LABEL_MISSED_OPPORTUNITY = "Missed Opportunity"
LABEL_EFFORT_DUPLICATION = "Effort Duplication"
LABEL_SPLIT = "Split(MO/ED)"
LABEL_ADDED_FILE = "Added File"
LABEL_DELETED_FILE = "Deleted File"
LABEL_UNINTERESTING = "Uninteresting"
LABEL_EVEN_DISTRIBUTION = "Even Distribution"
LABEL_NOT_APPLICABLE = "Not Applicable"

# Chart configuration
FIGURE_WIDTH = 15
FIGURE_HEIGHT = 10
FIGURE_DPI = 80
FONT_SIZE_LEGEND = 18
FONT_SIZE_AXIS_LABEL = 20
FONT_SIZE_TICK = 14
FONT_SIZE_TITLE = 20
GROUPED_FIGURE_WIDTH = 20
GROUPED_FIGURE_HEIGHT = 10


def all_class_bar(height: List[int], pr_nr: int, plotting: bool = False) -> None:
    """Generate a bar chart for basic patch classification categories.

    Args:
        height: List of frequency values for each classification.
        pr_nr: Pull request number for tracking.
        plotting: Whether to display the plot.
    """
    x_positions = [1, 2, 3, 4, 5]
    x_labels = ['PA', 'CC', 'NE', 'PN', 'ERROR']
    colors = [
        COLOR_PATCH_APPLIED,
        COLOR_CANNOT_CLASSIFY,
        COLOR_NOT_EXISTING,
        COLOR_PATCH_NOT_APPLIED,
        COLOR_ERROR
    ]

    plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    plt.bar(x_positions, height, tick_label=x_labels, width=0.8, color=colors)

    patches = [
        mpatches.Patch(color=COLOR_PATCH_APPLIED, label=LABEL_PATCH_APPLIED),
        mpatches.Patch(color=COLOR_CANNOT_CLASSIFY, label=LABEL_CANNOT_CLASSIFY),
        mpatches.Patch(color=COLOR_NOT_EXISTING, label=LABEL_NOT_EXISTING),
        mpatches.Patch(color=COLOR_PATCH_NOT_APPLIED, label=LABEL_PATCH_NOT_APPLIED),
        mpatches.Patch(color=COLOR_ERROR, label=LABEL_ERROR)
    ]

    plt.legend(fontsize=FONT_SIZE_LEGEND, loc="upper left", handles=patches)
    plt.xlabel('Classifications', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.ylabel('Frequency', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.xticks(fontsize=FONT_SIZE_TICK)
    plt.yticks(fontsize=FONT_SIZE_TICK)

    if plotting:
        plt.show()


def create_pie(slices: List[int], ax) -> None:
    """Create a pie chart for modification type distribution.

    Args:
        slices: Frequency values for each modification type.
        ax: Matplotlib pyplot module.
    """
    labels = ['MO', 'ED', 'SP', 'AF', 'DF']
    colors = ['r', 'y', 'g', 'b', 'c']

    ax.pie(slices, labels=labels, colors=colors,
           startangle=90, shadow=True, explode=(0, 0, 0, 0, 0),
           radius=1, autopct='%1.1f%%')
    ax.legend()


def create_bar(height: List[int], ax) -> None:
    """Create a bar chart for modification type distribution.

    Args:
        height: Frequency values for each modification type.
        ax: Matplotlib pyplot module.
    """
    x_positions = [1, 2, 3, 4, 5]
    x_labels = ['MO', 'ED', 'SP', 'AF', 'DF']
    colors = ['red', 'yellow', 'green', 'blue', 'cyan']

    ax.bar(x_positions, height, tick_label=x_labels, width=0.8, color=colors)
    ax.set_xlabel('Classifications', fontsize=FONT_SIZE_AXIS_LABEL)
    ax.set_ylabel('Frequency', fontsize=FONT_SIZE_AXIS_LABEL)


def grouped_bar_chart(y0: List[int], y1: List[int], y2: List[int], y3: List[int],
                       y4: List[int], y5: List[int], repo_nr: int) -> None:
    """Generate a grouped bar chart comparing multiple classification metrics.

    Args:
        y0: Missed Opportunity frequencies.
        y1: Effort Duplication frequencies.
        y2: Split (MO/ED) frequencies.
        y3: Added File frequencies.
        y4: Deleted File frequencies.
        y5: Uninteresting frequencies.
        repo_nr: Repository number for file naming.
    """
    bar_width = 0.15
    base_positions = np.arange(len(y0))
    position_offset_0 = base_positions
    position_offset_1 = [x + bar_width for x in position_offset_0]
    position_offset_2 = [x + bar_width for x in position_offset_1]
    position_offset_3 = [x + bar_width for x in position_offset_2]
    position_offset_4 = [x + bar_width for x in position_offset_3]
    position_offset_5 = [x + bar_width for x in position_offset_4]

    plt.figure(figsize=(GROUPED_FIGURE_WIDTH, GROUPED_FIGURE_HEIGHT), dpi=FIGURE_DPI)

    patches = [
        mpatches.Patch(color=COLOR_MISSED_OPPORTUNITY, label=LABEL_MISSED_OPPORTUNITY),
        mpatches.Patch(color=COLOR_EFFORT_DUPLICATION, label=LABEL_EFFORT_DUPLICATION),
        mpatches.Patch(color=COLOR_SPLIT, label=LABEL_SPLIT),
        mpatches.Patch(color=COLOR_ADDED_FILE, label=LABEL_ADDED_FILE),
        mpatches.Patch(color=COLOR_DELETED_FILE, label=LABEL_DELETED_FILE),
        mpatches.Patch(color=COLOR_UNINTERESTING, label=LABEL_UNINTERESTING)
    ]
    plt.legend(fontsize=FONT_SIZE_LEGEND, loc="upper left", handles=patches)

    plt.bar(position_offset_0, y0, color=COLOR_MISSED_OPPORTUNITY, width=bar_width, edgecolor='white')
    plt.bar(position_offset_1, y1, color=COLOR_EFFORT_DUPLICATION, width=bar_width, edgecolor='white')
    plt.bar(position_offset_2, y2, color=COLOR_SPLIT, width=bar_width, edgecolor='white')
    plt.bar(position_offset_3, y3, color=COLOR_ADDED_FILE, width=bar_width, edgecolor='white')
    plt.bar(position_offset_4, y4, color=COLOR_DELETED_FILE, width=bar_width, edgecolor='white')
    plt.bar(position_offset_5, y5, color=COLOR_UNINTERESTING, width=bar_width, edgecolor='white')

    plt.xlabel('Classifications', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.ylabel('Frequency', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.xticks(fontsize=FONT_SIZE_TICK)
    plt.yticks(fontsize=FONT_SIZE_TICK)

    interval_labels = ['0-100', '10-100', '20-100', '30-100', '40-100',
                      '50-100', '60-100', '70-100', '80-100', '90-100']
    plt.xticks([r + bar_width for r in range(len(y0))], interval_labels)

    plt.savefig(f"Plots/Grouped_bar_{repo_nr}.png", format="PNG", dpi=FIGURE_DPI, bbox_inches='tight')
    plt.show()


def create_all_bars(data: Dict, repo_nr: int) -> None:
    """Create a grid of bar charts for all intervals.

    Args:
        data: Dictionary mapping interval labels to frequency lists.
        repo_nr: Repository number for file naming.
    """
    fig = plt.figure(figsize=(GROUPED_FIGURE_WIDTH, GROUPED_FIGURE_HEIGHT))
    for idx, interval_label in enumerate(data, start=1):
        plt.subplot(2, 5, idx)
        plt.title(f"Bar Chart for interval {interval_label}", fontsize=FONT_SIZE_TITLE)
        create_bar(data[interval_label], plt)

    plt.savefig(f"Plots/All_Bars_{repo_nr}.png", format="PNG")
    plt.show()


def create_all_pie(data: Dict, repo_nr: int) -> None:
    """Create a grid of pie charts for all intervals.

    Args:
        data: Dictionary mapping interval labels to frequency lists.
        repo_nr: Repository number for file naming.
    """
    fig = plt.figure(figsize=(GROUPED_FIGURE_WIDTH, GROUPED_FIGURE_HEIGHT))
    for idx, interval_label in enumerate(data, start=1):
        plt.subplot(2, 5, idx)
        plt.title(f"Pie Chart for interval {interval_label}", fontsize=FONT_SIZE_TITLE)
        create_pie(data[interval_label], plt)

    plt.savefig(f"Plots/{repo_nr}_All_Pies.png", format="PNG")
    plt.show()


def all_class_bar_w_even_d(height: List[int], pr_nr: int) -> None:
    """Generate a bar chart for extended patch classification with even distribution.

    Args:
        height: List of frequency values for each classification.
        pr_nr: Pull request number for tracking.
    """
    x_positions = [1, 2, 3, 4, 5, 6, 7, 8]
    x_labels = ['MO', 'ED', 'Split(MO/ED)', 'CC', 'NE', 'NA', 'EVEN_D', 'ERROR']
    colors = [
        COLOR_MISSED_OPPORTUNITY,
        COLOR_EFFORT_DUPLICATION,
        COLOR_SPLIT,
        COLOR_CANNOT_CLASSIFY,
        COLOR_NOT_EXISTING,
        COLOR_NOT_APPLICABLE,
        COLOR_EVEN_DISTRIBUTION,
        COLOR_ERROR
    ]

    plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    plt.bar(x_positions, height, tick_label=x_labels, width=0.8, color=colors)

    patches = [
        mpatches.Patch(color=COLOR_MISSED_OPPORTUNITY, label=LABEL_MISSED_OPPORTUNITY),
        mpatches.Patch(color=COLOR_EFFORT_DUPLICATION, label=LABEL_EFFORT_DUPLICATION),
        mpatches.Patch(color=COLOR_SPLIT, label=LABEL_SPLIT),
        mpatches.Patch(color=COLOR_CANNOT_CLASSIFY, label=LABEL_CANNOT_CLASSIFY),
        mpatches.Patch(color=COLOR_NOT_EXISTING, label="Not Existing Files"),
        mpatches.Patch(color=COLOR_NOT_APPLICABLE, label=LABEL_NOT_APPLICABLE),
        mpatches.Patch(color=COLOR_EVEN_DISTRIBUTION, label=LABEL_EVEN_DISTRIBUTION),
        mpatches.Patch(color=COLOR_ERROR, label=LABEL_ERROR)
    ]

    plt.legend(fontsize=FONT_SIZE_LEGEND, loc="upper left", handles=patches)
    plt.xlabel('Classifications', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.ylabel('Frequency', fontsize=FONT_SIZE_AXIS_LABEL)
    plt.xticks(fontsize=FONT_SIZE_TICK)
    plt.yticks(fontsize=FONT_SIZE_TICK)

    plt.savefig(f"Plots/All_Classes_Bar_70_EVED_{pr_nr}.png", format="PNG",
                dpi=FIGURE_DPI, bbox_inches='tight')


def all_class_pie(slices: List[int], pr_nr: int, plotting: bool = False) -> None:
    """Generate a pie chart for patch classification distribution.

    Args:
        slices: Frequency values for each classification category.
        pr_nr: Pull request number for tracking.
        plotting: Whether to display the plot.
    """
    labels = ['Effort Duplication', 'Cannot Classify', 'Not Existing Files',
              'Not Applicable', 'Error']
    colors = [COLOR_EFFORT_DUPLICATION, COLOR_CANNOT_CLASSIFY, COLOR_NOT_EXISTING,
              COLOR_NOT_APPLICABLE, COLOR_ERROR]

    plt.pie(slices, labels=labels, colors=colors,
            startangle=0, shadow=True, explode=(0, 0, 0, 0, 0),
            radius=3, autopct='%1.1f%%')
    plt.rc('font', size=FONT_SIZE_LEGEND)
    plt.rc('legend', fontsize=FONT_SIZE_TICK)
    plt.legend(loc='center left', bbox_to_anchor=(2, 1.5))

    if plotting:
        plt.show()
