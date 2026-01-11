# Constants

## Overview

This page documents the constants and helpers defined in `analyzer.constant`.
It lists the public configuration values used across the analyzer and
documents the `EXTENSIONS` mapping and the `get_extension()` helper.

The documentation below reflects the current source in
`analyzer/constant.py`. For the authoritative API and inline source, see the
mkdocstrings reference at the bottom of this page.

## Public constants (from `analyzer.constant`)

| Constant | Default (code) | Purpose |
|---|---:|---|
| `GITHUB_API_BASE_URL` | `"https://api.github.com/repos/"` | Base URL for GitHub REST API repository requests. |
| `GITHUB_BASE_URL` | `"https://github.com/"` | Base URL for repository web links. |
| `GITHUB_RAW_URL` | `"https://raw.githubusercontent.com/"` | Base URL used to fetch raw file contents. |
| `NGRAM_SIZE` | `1` | Default n-gram size used by tokenization helpers/classifier. Often tuned per experiment. |
| `CONTEXT_LINE` | `10` | Number of context lines to preserve around hunks when rendering or matching. |
| `VERBOSE_MODE` | `False` | Default verbose flag; `analyzer.main` controls logging more robustly. |
| `MAGIC_COOKIE` | `None` | Reserved placeholder for opaque metadata or future features. |
| `BLOOMFILTER_SIZE` | `2097152` | Size used when building bloom filters (power-of-two value improves hashing performance). |
| `MIN_MN_RATIO` | `32` | Threshold used by some similarity heuristics (see callers for exact semantics). |
| `EXTENSIONS` | `Dict[str, str]` | Mapping from language/file identifiers to normalized extensions (no leading dot). See table and examples below. |

Refer to `analyzer.constant` for the full constant list and inline comments describing each value.

## `EXTENSIONS` mapping

`EXTENSIONS` maps common language identifiers or file-type labels to a preferred
file extension string used across the codebase (the strings never include a
leading dot). The mapping covers typical languages and variants, for example:

- `'python' -> 'py'`
- `'javascript' -> 'js'`, `'cjs' -> 'js'`, `'mjs' -> 'js'`
- `'typescript' -> 'ts'`, `'tsx' -> 'tsx'`
- `'yml' -> 'yaml'`

Use this mapping when normalizing filetypes or constructing filenames in
analysis pipelines.

## `get_extension(name: str) -> Optional[str]`

This helper returns the normalized extension (without a leading dot) for a
language identifier or a filename. Behavior:

- Accepts language identifiers (`'python'`) and returns `'py'` when present in
  `EXTENSIONS`.
- Accepts filenames such as `'file.py'` and extracts the suffix `'py'`.
- Accepts dotted extensions like `'.js'` and returns `'js'`.
- Returns `None` when the extension cannot be determined.

Examples (from the module docstring):

```python
get_extension('python')   # -> 'py'
get_extension('file.py')  # -> 'py'
get_extension('.js')      # -> 'js'
```

## Guidance and tuning notes
- `NGRAM_SIZE` default is `1` in the code — experiments typically increase
this value (e.g., 3–7) to tune the trade-off between recall and precision
- `BLOOMFILTER_SIZE` is a large power-of-two value for efficient bit-array
hashing; change only with an understanding of memory/false-positive tradeoffs.
- `CONTEXT_LINE` controls how much surrounding context is kept when showing
hunks; increase for debugging and decrease to compact outputs.

### Examples
Small snippet showing use of `get_extension` and constants:

```python
from analyzer import constant

print(constant.GITHUB_API_BASE_URL)
print(constant.NGRAM_SIZE)
print(constant.get_extension('file.py'))  # -> 'py'
```

## API Reference

::: analyzer.constant
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

## See Also

- [Classifier](classifier.md) - How tokenization and `NGRAM_SIZE` are used
- [Patch Loader](patch_loader.md) - How filenames and extensions are normalized
- [Main](main.md) - Where constants are applied at pipeline runtime