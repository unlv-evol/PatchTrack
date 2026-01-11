<!--
Reference documentation for the `main` module of PatchTrack.
This file provides a high-level overview, key functions, usage examples,
input/output formats, integration points, and best practices for maintainers
and contributors who need to understand how the `main` orchestration works.
-->

# Main Module

## Overview

The `main` module orchestrates the PatchTrack pipeline: loading patch and
source data, running classification, aggregating results, and invoking
analysis/visualization components. It exposes the primary CLI and programmatic
entry points used by end users and by the internal test harness.

This document complements the auto-generated API reference by explaining
typical workflows, configuration knobs, and practical examples for common
tasks.

## Purpose

- Provide a single entry point for running PatchTrack end-to-end
- Offer programmatic access for embedding PatchTrack into other tools or
	experiments
- Coordinate dataflow between `patch_loader`, `source_loader`, `classifier`,
	`aggregator`, and `analysis`

## Key Concepts

- Pipeline: The end-to-end sequence of steps from raw repository data to
	classification and visualization
- Configuration: Runtime parameters (verbosity, thresholds, output paths)
- Modes: `interactive` (notebook/REPL) vs `batch` (CLI/scripted)

## Important Constants and Defaults

- Default logging level: `INFO` (can be changed via `set_verbose_mode()`)
- Default thresholds: See `docs/reference/constant.md` for tuned values

## Primary Functions

- `main()` — CLI entry point that parses arguments and kicks off the pipeline.

- `run_pipeline(config: dict) -> dict` — Programmatic runner:
	- Loads patches and source files
	- Invokes classification and aggregation
	- Produces analysis outputs and returns a summary dictionary

- `set_verbose_mode(enabled: bool)` — Sets logging level (INFO when enabled,
	WARNING when disabled).

- `prepare_data(...)` — Internal helper to validate and pre-process inputs.

> Note: For full signatures and docstrings, see the auto-generated API
> reference produced by mkdocstrings.

## Usage Examples

### CLI (quick start)

Run the full pipeline with default settings:

```bash
python PatchTrack.py run --input path/to/data --output results/
```

Enable verbose logging to see progress messages:

```bash
python PatchTrack.py run --input path/to/data --output results/ --verbose
```

### Programmatic (Python)

```python
from analyzer.main import run_pipeline, set_verbose_mode

set_verbose_mode(True)

config = {
		"patchs_path": "data/patches.json",
		"source_dir": "data/src",
		"output_dir": "results",
}

summary = run_pipeline(config)
print(summary["aggregate_summary"])  # high-level counts and metrics
```

## Input / Output Formats

- Input patch files: JSON or ndjson produced by the `dataprep` stage. Each
	patch record typically contains: `repo`, `pr_number`, `file_path`, `hunks`,
	`diff`, and metadata.
- Source files: Directory tree of repository sources used for matching.
- Output: A results folder containing:
	- `classifications.json` — per-file/per-patch classification results
	- `aggregated.json` — per-PR aggregated decisions
	- Plots and CSV exports produced by the `analysis` module

Example `run_pipeline` return value (summary):

```json
{
	"processed_patches": 1250,
	"classified_pairs": 1187,
	"aggregate_summary": {"PA": 430, "PN": 530, "NE": 227},
	"output_dir": "results/2026-01-10"
}
```

## Integration Points

- `patch_loader` — Supplies normalized patch records
- `source_loader` — Supplies source token/hashes used during matching
- `classifier` — Performs per-patch matching and labels (PA/PN/NE)
- `aggregator` — Collates per-file decisions into PR-level decisions
- `analysis` — Generates visualizations and metrics

When modifying the `main` orchestration, ensure inputs/outputs between these
modules remain compatible (see `docs/reference/patch_loader.md` and
`docs/reference/source_loader.md`).

## Configuration and Tuning

- Use the `config` dict passed to `run_pipeline` to override defaults. Key
	fields include:
	- `min_commits_threshold`
	- `ngram_size`
	- `similarity_threshold`
	- `output_dir`

- Performance tuning:
	- Increase `ngram_size` to reduce false positives at cost of recall
	- Increase `similarity_threshold` to be more conservative in matches

## Best Practices

- Run the `dataprep` stage to normalize patches before invoking `main`.
- Use batching when processing large repositories to avoid excessive memory
	usage.
- Keep `output_dir` structured by timestamp to avoid overwriting results.
- When debugging, use `set_verbose_mode(True)` to enable `INFO` logs.

## Troubleshooting

- No classifications produced: verify input files exist and are correctly
	formatted (see `dataprep` output).  
- Low recall / many NE labels: consider lowering `ngram_size` or
	`similarity_threshold`.  
- High false positives: increase `ngram_size` and review `classifier` logs.

## Maintainer Notes

- Keep the CLI flags and the programmatic `config` in sync.  
- Update examples in this file when you introduce new config fields.  
- Ensure mkdocstrings picks up any signature changes in `analyzer.main`.

## API Reference

::: analyzer.main
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

<!--
The API reference above is generated by mkdocstrings at build time. If you
don't see the API when previewing locally, make sure `mkdocs` + `mkdocstrings`
are installed and run `mkdocs serve` to regenerate the pages.
-->

## See Also

- [Getting Started](../getting_started.md) — Installation and Quick Start
- [Classifier](classifier.md) — Classification algorithm and decisions
- [Aggregator](aggregator.md) — Aggregation rules and examples
- [Analysis](analysis.md) — Visualization & metrics
