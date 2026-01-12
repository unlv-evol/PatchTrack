"""Helper utilities for PatchTrack analysis.

Provides functions for API requests, file handling, comment removal,
and type detection across multiple programming languages.
"""

from typing import List, Optional, Dict, Any
from functools import wraps
from time import time
import json
import os
import sys
import re

import pandas as pd
import requests
from dateutil import parser
from datetime import datetime, timedelta

from . import constant
from . import common

def unique(items: List) -> List:
    """Get unique items from a list while preserving order.

    Args:
        items: Input list with potential duplicates.

    Returns:
        List with duplicate entries removed.
    """
    unique_list = pd.Series(items).drop_duplicates().to_list()
    return unique_list

def api_request(url: str, token: str) -> Any:
    """Make an authenticated API request to GitHub.

    Args:
        url: The URL endpoint to request.
        token: GitHub API token for authentication.

    Returns:
        Parsed JSON response or response object on error.
    """
    header = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=header)
    try:
        json_response = json.loads(response.content)
        return json_response
    except Exception:
        return response

def get_response(url: str, token_list: List[str], ct: int) -> tuple:
    """Retrieve JSON response from API endpoint using token rotation.

    Args:
        url: API endpoint URL.
        token_list: List of available GitHub API tokens.
        ct: Current token index counter.

    Returns:
        Tuple of (json_data, updated_token_counter).
    """
    json_data = None
    len_tokens = len(token_list)

    try:
        ct = ct % len_tokens
        headers = {'Authorization': f'Bearer {token_list[ct]}'}
        request = requests.get(url, headers=headers)
        json_data = json.loads(request.content)
        ct += 1
    except Exception as e:
        print(f"Error in get_response: {e}")

    return json_data, ct

def file_name(name: str) -> str:
    """Extract the file name from a file path.

    Args:
        name: File path or name string.

    Returns:
        Extracted file name.
    """
    if name.startswith('.'):
        return name[1:]
    elif '/' in name:
        return name.split('/')[-1]
    else:
        return name


def file_dir(name: str) -> str:
    """Extract the directory path from a file path.

    Args:
        name: File path string.

    Returns:
        Directory path (empty string if no directory).
    """
    if name.startswith('.'):
        return name[1]
    elif '/' in name:
        return '/'.join(name.split('/')[:-1])
    else:
        return ''
    

def save_file(file: bytes, storage_dir: str, file_name: str) -> None:
    """Save binary file to specified directory.

    Args:
        file: Binary file content.
        storage_dir: Directory path for storage.
        file_name: Name of file to save.
    """
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    file_path = os.path.join(storage_dir, file_name)
    mode = 'xb' if not os.path.exists(file_path) else 'wb'

    with open(file_path, mode) as f:
        f.write(file)


# File extension mapping for language detection (lazy initialized to avoid circular import)
_EXTENSION_MAP = None

def _get_extension_map():
    """Get extension map, initializing on first use to avoid circular imports."""
    global _EXTENSION_MAP
    if _EXTENSION_MAP is None:
        _EXTENSION_MAP = {
            'c': common.FileExt.C,
            'h': common.FileExt.C,
            'cpp': common.FileExt.C,
            'java': common.FileExt.Java,
            'cs': common.FileExt.Java,
            'sh': common.FileExt.ShellScript,
            'pl': common.FileExt.Perl,
            'py': common.FileExt.Python,
            'php': common.FileExt.PHP,
            'rb': common.FileExt.Ruby,
            'js': common.FileExt.JavaScript,
            'jsx': common.FileExt.JavaScript,
            'ts': common.FileExt.JavaScript,
            'vue': common.FileExt.JavaScript,
            'svelte': common.FileExt.JavaScript,
            'scala': common.FileExt.Scala,
            'yaml': common.FileExt.yaml,
            'yml': common.FileExt.yaml,
            'ipynb': common.FileExt.ipynb,
            'json': common.FileExt.JSON,
            'kt': common.FileExt.Kotlin,
            'gradle': common.FileExt.gradle,
            'gemfile': common.FileExt.GEMFILE,
            'xml': common.FileExt.Xml,
            'md': common.FileExt.markdown,
            'go': common.FileExt.goland,
            'css': common.FileExt.CSS,
            'html': common.FileExt.html,
            'fs': common.FileExt.Fsharp,
            'regex': common.FileExt.REGEX,
            'conf': common.FileExt.conf,
            'swift': common.FileExt.SWIFT,
            'rs': common.FileExt.RUST,
            'sql': common.FileExt.SQL,
            'tsx': common.FileExt.TSX,
            'sol': common.FileExt.SOLIDITY,
            'vb': common.FileExt.VB,
        }
    return _EXTENSION_MAP

_SPECIAL_FILES = {'requirements.txt', 'requirement.txt'}


def get_file_type(file_path: str) -> int:
    """Detect file type based on extension.

    Args:
        file_path: Path or name of the file.

    Returns:
        FileExt enum value indicating the file type.
    """
    name = file_name(file_path)

    if name.lower() in _SPECIAL_FILES:
        return common.FileExt.REQ_TXT

    ext = file_path.split('.')[-1].lower()
    return _get_extension_map().get(ext, common.FileExt.Text)

def _preserve_newlines(match_text: str) -> str:
    """Preserve newlines in match by replacing with newline characters.

    Args:
        match_text: Text containing newlines.

    Returns:
        Replacement string with preserved newlines.
    """
    return '\n' * match_text.count('\n')


def _extract_noncomments(source: str, regex_pattern) -> str:
    """Extract non-comment parts from source using regex pattern.

    Args:
        source: Source code text.
        regex_pattern: Compiled regex pattern for comment removal.

    Returns:
        Source with comments removed.
    """
    return ''.join([m.group('noncomment') for m in regex_pattern.finditer(source)
                   if m.group('noncomment')])


def _extract_noncomments_with_newlines(source: str, regex_pattern) -> str:
    """Extract non-comment parts, preserving newlines from multiline comments.

    Args:
        source: Source code text.
        regex_pattern: Compiled regex pattern for comment removal.

    Returns:
        Source with comments removed and newlines preserved.
    """
    lines = []
    for match in regex_pattern.finditer(source):
        if match.group('noncomment'):
            lines.append(match.group('noncomment'))
        elif match.group('multilinecomment'):
            lines.append(_preserve_newlines(match.group('multilinecomment')))
    return ''.join(lines)


def remove_comment(source: str, file_ext: int) -> str:
    """Remove comments from source code based on file type.

    Args:
        source: Source code text.
        file_ext: FileExt enum value indicating language type.

    Returns:
        Source code with comments removed.
    """
    # C-like languages (C, Java, Go, CSS)
    if file_ext in [common.FileExt.C, common.FileExt.Java, common.FileExt.goland, common.FileExt.CSS]:
        source = _extract_noncomments_with_newlines(source, common.C_REGEX)

    # Python and config files
    elif file_ext in [common.FileExt.Python, common.FileExt.conf]:
        source = _extract_noncomments(source, common.PY_REGEX)
        source = _extract_noncomments(source, common.PY_MULTILINE_1_REGEX)
        source = _extract_noncomments(source, common.PY_MULTILINE_2_REGEX)

    # Shell scripts
    elif file_ext == common.FileExt.ShellScript:
        source = _extract_noncomments(source, common.SHELLSCRIPT_REGEX)

    # Perl
    elif file_ext == common.FileExt.Perl:
        source = _extract_noncomments(source, common.PERL_REGEX)

    # SQL
    elif file_ext == common.FileExt.SQL:
        source = _extract_noncomments(source, common.SQL_REGEX)

    # Rust
    elif file_ext == common.FileExt.RUST:
        source = _extract_noncomments(source, common.RUST_REGEX)

    # TypeScript/TSX
    elif file_ext == common.FileExt.TSX:
        source = _extract_noncomments(source, common.TSX_REGEX)

    # Solidity
    elif file_ext == common.FileExt.SOLIDITY:
        source = _extract_noncomments(source, common.SOLIDITY_REGEX)

    # Visual Basic
    elif file_ext == common.FileExt.VB:
        source = _extract_noncomments(source, common.VB_REGEX)

    # PHP
    elif file_ext == common.FileExt.PHP:
        source = _extract_noncomments_with_newlines(source, common.PHP_REGEX)

    # Ruby
    elif file_ext in [common.FileExt.Ruby, common.FileExt.GEMFILE]:
        source = _extract_noncomments_with_newlines(source, common.RUBY_REGEX)

    # JavaScript-like languages
    elif file_ext in [common.FileExt.Scala, common.FileExt.JavaScript, common.FileExt.TypeScript,
                      common.FileExt.Kotlin, common.FileExt.gradle, common.FileExt.svelte]:
        source = _extract_noncomments(source, common.JS_REGEX)
        source = _extract_noncomments(source, common.JS_PARTIAL_COMMENT_REGEX)

    # YAML
    elif file_ext == common.FileExt.yaml:
        source = _extract_noncomments(source, common.YAML_REGEX)
        source = re.sub(common.YAML_DOUBLE_QUOTE_REGEX, "", source)
        source = re.sub(common.YAML_SINGLE_QUOTE_REGEX, "", source)

    # Jupyter Notebook
    elif file_ext == common.FileExt.ipynb:
        json_data = json.loads(source)
        python_code = ''

        for cell in json_data['cells']:
            for line in cell['source']:
                python_code += line if line.endswith('\n') else line + '\n'

        source = _extract_noncomments(python_code, common.PY_REGEX)
        source = _extract_noncomments(source, common.PY_MULTILINE_1_REGEX)
        source = _extract_noncomments(source, common.PY_MULTILINE_2_REGEX)

    # JSON
    elif file_ext == common.FileExt.JSON:
        source = common.WHITESPACE_REGEX.sub("", source)
        source = source.lower()

    # XML-like languages
    elif file_ext in [common.FileExt.Xml, common.FileExt.markdown, common.FileExt.html]:
        source = _extract_noncomments(source, common.XML_REGEX)

    return source


# Backwards-compatible alias: some modules call `remove_comments`
def remove_comments(source: str, file_ext: int) -> str:
    """Alias for `remove_comment` to maintain backward compatibility."""
    return remove_comment(source, file_ext)

def timing(func):
    """Decorator to measure and print function execution time.

    Args:
        func: Function to decorate.

    Returns:
        Decorated function with timing output.
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        elapsed = end_time - start_time
        print(f'func: {func.__name__} args: [{args}, {kwargs}] took: {elapsed:.4f} sec')
        return result

    return wrap


def count_loc(file_path: str) -> int:
    """Count total lines of code in a file.

    Args:
        file_path: Path to the file.

    Returns:
        Total number of lines in the file.
    """
    with open(file_path, 'r') as f:
        return sum(1 for _ in f)