# Helpers

This page documents the `analyzer.helpers` utilities used across PatchTrack.

The module provides small, well-scoped helpers for common tasks used by the
analysis pipeline: API request handling, file and path utilities, comment
removal for many languages, light-weight timing instrumentation, and simple
file I/O helpers.

## Notes
- The module uses a lazy `_get_extension_map()` helper to avoid import-time
  circular dependencies with `analyzer.common`.
- The `remove_comments` alias exists for backward compatibility — call either
  `remove_comment` or `remove_comments`.

## Examples

Remove comments from a Python source string:

```python
from analyzer import helpers, common

code = """# comment\nprint('hello')\n"""
clean = helpers.remove_comment(code, common.FileExt.Python)
print(clean)
```

Get the file type for a filename and count lines in a file:

```python
ft = helpers.get_file_type('app.py')
lines = helpers.count_loc('/path/to/file.py')
```

Use the `timing` decorator to measure function time:

```python
from analyzer.helpers import timing

@timing
def expensive():
    # work
    pass

expensive()
```

## API Reference

::: analyzer.helpers
    handler: python
    options:
      show_root_heading: false
      show_source: true
      show_object_full_path: true
      members_order: source

## See Also

- [Patch Loader](patch_loader.md) - Parses PR patches
- [Source Loader](source_loader.md) - Parses ChatGPT code
- [Classifier](classifier.md) - Uses n-gram configuration
- [Common](common.md) - Configuration (n-gram size, etc.)