
"""Project-wide constants used by the analyzer.

This module centralizes immutable configuration values such as GitHub
endpoints and default analysis parameters.

Small helpers are provided to normalize and lookup file extensions from
language identifiers or filenames.
"""

from typing import Dict, Optional

# Public API
__all__ = [
    "GITHUB_API_BASE_URL",
    "GITHUB_BASE_URL",
    "GITHUB_RAW_URL",
    "NGRAM_SIZE",
    "CONTEXT_LINE",
    "VERBOSE_MODE",
    "MAGIC_COOKIE",
    "BLOOMFILTER_SIZE",
    "MIN_MN_RATIO",
    "EXTENSIONS",
    "get_extension",
]

# GitHub endpoints
GITHUB_API_BASE_URL: str = "https://api.github.com/repos/"
GITHUB_BASE_URL: str = "https://github.com/"
GITHUB_RAW_URL: str = "https://raw.githubusercontent.com/"

# Default analysis parameters
NGRAM_SIZE: int = 1  # default
CONTEXT_LINE: int = 10
VERBOSE_MODE: bool = False
MAGIC_COOKIE = None
BLOOMFILTER_SIZE: int = 2_097_152
MIN_MN_RATIO: int = 32

# Mapping from language or file-type identifiers to preferred file extensions.
# Keys are common identifiers encountered in metadata; values are normalized
# extension strings used across the codebase (no leading dot).
EXTENSIONS: Dict[str, str] = {
    "bash": "sh",
    "c": "c",
    "csharp": "cs",
    "cpp": "cpp",
    "css": "css",
    "elixir": "exs",
    "fsharp": "fs",
    "gitignore": "gitignore",
    "go": "go",
    "html": "html",
    "ipynb": "ipynb",
    "java": "java",
    "javascript": "js",
    "jsx": "jsx",
    "json": "json",
    "kotlin": "kt",
    "liquid": "liquid",
    "markdown": "md",
    "cjs": "js",
    "mjs": "js",
    "perl": "pl",
    "php": "php",
    "python": "py",
    "react": "jsx",
    "rust": "rs",
    "scala": "scala",
    "sh": "sh",
    "svelte": "svelte",
    "swift": "swift",
    "solidity": "sol",
    "sql": "sql",
    "tsx": "tsx",
    "typescript": "ts",
    "vue": "vue",
    "xml": "xml",
    "yaml": "yaml",
    "yml": "yaml",
    "gradle": "gradle",
    "regex": "regex",
    "nginx": "conf",
}


def get_extension(name: str) -> Optional[str]:
    """Return the normalized extension for a language identifier or filename.

    The returned extension does not include a leading dot (e.g. 'py').

    Examples:
        get_extension('python') -> 'py'
        get_extension('file.py')  -> 'py'
        get_extension('.js')     -> 'js'

    Returns ``None`` when the extension cannot be determined.
    """
    if not name:
        return None

    key = name.strip().lower()

    # If a filename or dotted extension is provided, extract the suffix
    if "." in key and not key.startswith("."):
        key = key.rsplit(".", 1)[-1]

    # Strip leading dot ('.py' -> 'py')
    if key.startswith("."):
        key = key[1:]

    return EXTENSIONS.get(key)
