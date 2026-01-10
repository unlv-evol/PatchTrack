"""
Common variables and functions for patch analysis.

Initial version by Jiyong Jang, 2012
Modified by Daniel Ogenrwot, 2023
"""

import pickle
import re
from typing import Any, Optional
from collections import namedtuple

from . import constant
from . import helpers


# Global configuration variables (mirrors values from `analyzer.constant`)
ngram_size: int = constant.NGRAM_SIZE
context_line: int = constant.CONTEXT_LINE
verbose_mode: bool = constant.VERBOSE_MODE
magic_cookie = constant.MAGIC_COOKIE
bloomfilter_size: int = constant.BLOOMFILTER_SIZE
min_mn_ratio: int = constant.MIN_MN_RATIO

# Named tuples for data structures
PatchInfo = namedtuple(
    'PatchInfo',
    ['file_path', 'file_ext', 'orig_lines', 'norm_lines', 'hash_list', 'patch_hashes', 'ngram_size']
)
SourceInfo = namedtuple(
    'SourceInfo',
    ['file_path', 'file_ext', 'orig_lines', 'norm_lines']
)
ContextInfo = namedtuple(
    'ContextInfo',
    ['source_id', 'prev_context_line', 'start_line', 'end_line', 'next_context_line']
)


class FileExt:
    """Index for file types supported by the tool."""

    NonText = 0
    Text = 1
    C = 2
    Java = 3
    ShellScript = 4
    Python = 5
    Perl = 6
    PHP = 7
    Ruby = 8
    yaml = 9
    Scala = 10
    ipynb = 11
    JavaScript = 12
    JSON = 13
    Kotlin = 14
    Xml = 15
    gradle = 16
    GEMFILE = 17
    REQ_TXT = 18
    TypeScript = 19
    CPP = 20
    CSHARP = 21
    VUE = 22
    REACT = 23
    Bash = 24
    markdown = 25
    goland = 26
    html = 27
    CSS = 28
    Fsharp = 29
    REGEX = 30
    conf = 31
    svelte = 32
    TSX = 33
    SQL = 34
    SWIFT = 35
    RUST = 36
    SOLIDITY = 37
    VB = 38


# HTML escape character mapping
HTML_ESCAPE_DICT = {
    '&': '&amp;',
    '>': '&gt;',
    '<': '&lt;',
    '"': '&quot;',
    '\'': '&apos;'
}


# Regular expressions for comment detection
# C, Java, Go style comments
C_REGEX = re.compile(
    r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)
C_PARTIAL_COMMENT_REGEX = re.compile(
    r'(?P<comment>/\*.*?$|^.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"{}\s]*)',
    re.DOTALL
)

# Shell script and Bash style comments
SHELLSCRIPT_REGEX = re.compile(
    r'(?P<comment>#.*?$)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#\'"]*)' ,
    re.DOTALL | re.MULTILINE
)

# Swift style comments
SWIFT_REGEX = re.compile(
    r'(?P<comment>//.*?$|/\*[\s\S]*?\*/|/\*.*?$|^.*?\*/)|'
    r'(?P<noncomment>[^/\n]*[^\n]*)' ,
    re.DOTALL | re.MULTILINE
)

# Rust style comments
RUST_REGEX = re.compile(
    r'(?P<comment>//.*?$|///.*?$|/\*[\s\S]*?\*/|/\*.*?$|^.*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)

# TSX/TypeScript JSX style comments
TSX_REGEX = re.compile(
    r'(?P<comment>//.*?$|/\*[\s\S]*?\*/|/\*.*?$|^.*?\*/|/\*\*[\s\S]*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)

# SQL style comments
SQL_REGEX = re.compile(
    r'(?P<comment>--.*?$|/\*[\s\S]*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'\"-]*)' ,
    re.DOTALL | re.MULTILINE
)

# Perl style comments
PERL_REGEX = re.compile(
    r'(?P<comment>#.*?$|[{}]+)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#\'"{}\s]*)' ,
    re.DOTALL | re.MULTILINE
)

# PHP style comments
PHP_REGEX = re.compile(
    r'(?P<comment>#.*?$|//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#/\'"{}\s]*)' ,
    re.DOTALL | re.MULTILINE
)

# Ruby and Gemfile style comments
RUBY_REGEX = re.compile(
    r'(?P<comment>#.*?$)|(?P<multilinecomment>=begin.*?=end)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#=\'"]*)',
    re.DOTALL | re.MULTILINE
)
RUBY_PARTIAL_COMMENT_REGEX = re.compile(
    r'(?P<comment>=begin.*?$|^.*?=end)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#=\'"]*)' ,
    re.DOTALL
)

# YAML style comments
YAML_REGEX = re.compile(
    r'(?P<comment>#.*?$)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#\'"]*)' ,
    re.DOTALL | re.MULTILINE
)
YAML_DOUBLE_QUOTE_REGEX = re.compile(r'["]+')
YAML_SINGLE_QUOTE_REGEX = re.compile(r"[']+")

# JavaScript, Scala, C++, Kotlin, Gradle, C#, Vue, JSX style comments
JS_REGEX = re.compile(
    r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)
JS_PARTIAL_COMMENT_REGEX = re.compile(
    r'(?P<comment>/\*.*?$|^.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"{}]*)' ,
    re.DOTALL
)

# Python style comments
PY_REGEX = re.compile(
    r'(?P<comment>#.*?$)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^#\'"]*)',
    re.DOTALL | re.MULTILINE
)
PY_MULTILINE_1_REGEX = re.compile(
    r'(?P<multilinecomment>""".*?""")|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)',
    re.DOTALL | re.MULTILINE
)
PY_MULTILINE_2_REGEX = re.compile(
    r"(?P<multilinecomment>'''.*?''')|(?P<noncomment>'(\\.|[^\\'])*'|\"(\\.|[^\"])*\"|.[^/'\"]*)' ,",
    re.DOTALL | re.MULTILINE
)

# XML and Markdown style comments
XML_REGEX = re.compile(
    r'(?P<multilinecomment><!--.*?-->)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)

# Solidity style comments
SOLIDITY_REGEX = re.compile(
    r'(?P<comment>//.*?$|/\*[\s\S]*?\*/|/\*.*?$|^.*?\*/)|'
    r'(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)' ,
    re.DOTALL | re.MULTILINE
)

# Visual Basic style comments
VB_REGEX = re.compile(
    r"(?P<comment>'[^\n]*$|REM[^\n]*$)|(?P<noncomment>\"(\\.|[^\"])*\"|.[^'\"R]*)",
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)

# Regular expression for whitespace (excluding newlines)
WHITESPACE_REGEX = re.compile(r'[\t\x0b\x0c\r ]+')


# Hash functions
def fnv1a_hash(string):
    """
    FNV-1a 32-bit hash (http://isthe.com/chongo/tech/comp/fnv/).

    Args:
        string (str): The string to be hashed.

    Returns:
        int: The hash value.
    """
    hash_value = 2166136261
    for c in string:
        hash_value ^= ord(c)
        hash_value *= 16777619
        hash_value &= 0xFFFFFFFF
    return hash_value


def djb2_hash(string: str) -> int:
    """
    djb2 hash (http://www.cse.yorku.ca/~oz/hash.html).

    Args:
        string (str): The string to be hashed.

    Returns:
        int: The hash value.
    """
    hash_value = 5381
    for c in string:
        hash_value = ((hash_value << 5) + hash_value) + ord(c)
        hash_value &= 0xFFFFFFFF
    return hash_value


def sdbm_hash(string: str) -> int:
    """
    sdbm hash (http://www.cse.yorku.ca/~oz/hash.html).

    Args:
        string (str): The string to be hashed.

    Returns:
        int: The hash value.
    """
    hash_value = 0
    for c in string:
        hash_value = ord(c) + (hash_value << 6) + (hash_value << 16) - hash_value
        hash_value &= 0xFFFFFFFF
    return hash_value


def file_type(file_path: str) -> Any:
    """Get the file type of the given file path.

    Delegates to `helpers.get_file_type`.
    """
    return helpers.get_file_type(file_path)


def verbose_print(text: str) -> None:
    """Print text when `verbose_mode` is set.

    Kept as a small helper for compatibility with existing call sites.
    """
    if verbose_mode:
        print(text)


# Pickle file I/O functions
def _repo_pickle_path(pair_nr: int, source: str, folder: str, suffix: str) -> str:
    """Construct a repo-scoped pickle filename.

    `source` is expected in the form 'org/repo'.
    """
    org, repo = source.split('/')
    return f"{folder}/{pair_nr}_{org}_{repo}_{suffix}.pkl"


def read_prs(pair_nr: int, source: str) -> Any:
    """
    Load pull request data from pickle file.

    Args:
        pair_nr (int): The pair number.
        source (str): The source in 'org/repo' format.

    Returns:
        dict: The loaded pull request data.
    """
    file_path = _repo_pickle_path(pair_nr, source, "Repos_prs", "prs")
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def read_results(pair_nr: int, source: str) -> Any:
    """
    Load results data from pickle file.

    Args:
        pair_nr (int): The pair number.
        source (str): The source in 'org/repo' format.

    Returns:
        dict: The loaded results data.
    """
    file_path = _repo_pickle_path(pair_nr, source, "Repos_results", "results")
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def read_totals(pair_nr: int, source: str) -> Any:
    """
    Load metrics/totals data from pickle file.

    Args:
        pair_nr (int): The pair number.
        source (str): The source in 'org/repo' format.

    Returns:
        dict: The loaded metrics data.
    """
    file_path = _repo_pickle_path(pair_nr, source, "Repos_totals", "totals")
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def pickle_file(file_path: str, data: object) -> None:
    """
    Save data to a pickle file.

    Args:
        file_path (str): The file path (without .pkl extension).
        data: The data to pickle.
    """
    with open(f"{file_path}.pkl", 'wb') as f:
        pickle.dump(data, f)
