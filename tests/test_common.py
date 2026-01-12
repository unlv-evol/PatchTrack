"""Unit tests for analyzer.common module.

Tests the common module including:
- Hash functions (FNV-1a, DJB2, SDBM)
- Named tuples (PatchInfo, SourceInfo, ContextInfo)
- FileExt class for file type constants
- Global configuration variables
"""

import pytest
from analyzer import common


class TestHashFunctions:
    """Test hash function implementations."""

    def test_fnv1a_hash_consistency(self):
        """Test FNV-1a hash produces consistent results."""
        test_string = "hello_world"
        hash1 = common.fnv1a_hash(test_string)
        hash2 = common.fnv1a_hash(test_string)
        assert hash1 == hash2

    def test_fnv1a_hash_returns_int(self):
        """Test FNV-1a hash returns an integer."""
        assert isinstance(common.fnv1a_hash("test"), int)

    def test_fnv1a_hash_different_inputs_different_hashes(self):
        """Test FNV-1a hash differs for different inputs."""
        hash1 = common.fnv1a_hash("hello")
        hash2 = common.fnv1a_hash("world")
        assert hash1 != hash2

    def test_fnv1a_hash_empty_string(self):
        """Test FNV-1a hash handles empty string."""
        result = common.fnv1a_hash("")
        assert isinstance(result, int)

    def test_fnv1a_hash_special_characters(self):
        """Test FNV-1a hash handles special characters."""
        result = common.fnv1a_hash("!@#$%^&*()")
        assert isinstance(result, int)

    def test_djb2_hash_consistency(self):
        """Test DJB2 hash produces consistent results."""
        test_string = "patch_matching"
        hash1 = common.djb2_hash(test_string)
        hash2 = common.djb2_hash(test_string)
        assert hash1 == hash2

    def test_djb2_hash_returns_int(self):
        """Test DJB2 hash returns an integer."""
        assert isinstance(common.djb2_hash("test"), int)

    def test_djb2_hash_different_inputs(self):
        """Test DJB2 hash differs for different inputs."""
        hash1 = common.djb2_hash("foo")
        hash2 = common.djb2_hash("bar")
        assert hash1 != hash2

    def test_djb2_hash_empty_string(self):
        """Test DJB2 hash handles empty string."""
        result = common.djb2_hash("")
        assert isinstance(result, int)

    def test_sdbm_hash_consistency(self):
        """Test SDBM hash produces consistent results."""
        test_string = "source_code"
        hash1 = common.sdbm_hash(test_string)
        hash2 = common.sdbm_hash(test_string)
        assert hash1 == hash2

    def test_sdbm_hash_returns_int(self):
        """Test SDBM hash returns an integer."""
        assert isinstance(common.sdbm_hash("test"), int)

    def test_sdbm_hash_different_inputs(self):
        """Test SDBM hash differs for different inputs."""
        hash1 = common.sdbm_hash("abc")
        hash2 = common.sdbm_hash("def")
        assert hash1 != hash2

    def test_sdbm_hash_empty_string(self):
        """Test SDBM hash handles empty string."""
        result = common.sdbm_hash("")
        assert isinstance(result, int)

    def test_hash_functions_produce_different_values_for_same_input(self):
        """Test that different hash functions produce different values."""
        test_str = "ngram_test"
        h1 = common.fnv1a_hash(test_str)
        h2 = common.djb2_hash(test_str)
        h3 = common.sdbm_hash(test_str)
        # Hash functions should generally produce different values
        assert not (h1 == h2 and h2 == h3)


class TestFileExt:
    """Test FileExt class for file type constants."""

    def test_fileext_constants_exist(self):
        """Test that common file extension constants are defined."""
        assert hasattr(common.FileExt, 'Python')
        assert hasattr(common.FileExt, 'Java')
        assert hasattr(common.FileExt, 'JavaScript')
        assert hasattr(common.FileExt, 'C')

    def test_fileext_values_are_integers(self):
        """Test that FileExt values are integers."""
        assert isinstance(common.FileExt.Python, int)
        assert isinstance(common.FileExt.Java, int)
        assert isinstance(common.FileExt.JavaScript, int)

    def test_fileext_values_are_unique(self):
        """Test that FileExt values are unique."""
        fileext_dict = {
            k: v for k, v in vars(common.FileExt).items()
            if not k.startswith('_')
        }
        values = list(fileext_dict.values())
        # Check uniqueness
        assert len(values) == len(set(values))

    def test_fileext_python_value(self):
        """Test Python file extension constant."""
        assert common.FileExt.Python == 5

    def test_fileext_java_value(self):
        """Test Java file extension constant."""
        assert common.FileExt.Java == 3

    def test_fileext_javascript_value(self):
        """Test JavaScript file extension constant."""
        assert common.FileExt.JavaScript == 12


class TestGlobalConfigVariables:
    """Test global configuration variables."""

    def test_ngram_size_is_integer(self):
        """Test ngram_size is an integer."""
        assert isinstance(common.ngram_size, int)
        assert common.ngram_size >= 1

    def test_context_line_is_integer(self):
        """Test context_line is an integer."""
        assert isinstance(common.context_line, int)
        assert common.context_line > 0

    def test_verbose_mode_is_boolean(self):
        """Test verbose_mode is a boolean."""
        assert isinstance(common.verbose_mode, bool)

    def test_bloomfilter_size_is_integer(self):
        """Test bloomfilter_size is an integer."""
        assert isinstance(common.bloomfilter_size, int)
        assert common.bloomfilter_size > 0

    def test_min_mn_ratio_is_integer(self):
        """Test min_mn_ratio is an integer."""
        assert isinstance(common.min_mn_ratio, int)
        assert common.min_mn_ratio > 0

    def test_magic_cookie_exists(self):
        """Test magic_cookie variable exists."""
        assert hasattr(common, 'magic_cookie')


class TestNamedTuples:
    """Test named tuple data structures."""

    def test_patchinfo_creation(self):
        """Test PatchInfo namedtuple can be created."""
        patch = common.PatchInfo(
            file_path="test.py",
            file_ext=5,
            orig_lines="print('hello')",
            norm_lines=["print", "hello"],
            hash_list=[123, 456, 789],
            patch_hashes=[("hello", [123, 456, 789])],
            ngram_size=1
        )
        assert patch.file_path == "test.py"
        assert patch.file_ext == 5
        assert patch.ngram_size == 1

    def test_patchinfo_fields(self):
        """Test PatchInfo has correct fields."""
        fields = common.PatchInfo._fields
        expected = ('file_path', 'file_ext', 'orig_lines', 'norm_lines',
                   'hash_list', 'patch_hashes', 'ngram_size')
        assert fields == expected

    def test_sourceinfo_creation(self):
        """Test SourceInfo namedtuple can be created."""
        source = common.SourceInfo(
            file_path="example.py",
            file_ext=5,
            orig_lines="x = 1",
            norm_lines=["x", "1"]
        )
        assert source.file_path == "example.py"
        assert source.file_ext == 5

    def test_sourceinfo_fields(self):
        """Test SourceInfo has correct fields."""
        fields = common.SourceInfo._fields
        expected = ('file_path', 'file_ext', 'orig_lines', 'norm_lines')
        assert fields == expected

    def test_contextinfo_creation(self):
        """Test ContextInfo namedtuple can be created."""
        context = common.ContextInfo(
            source_id=1,
            prev_context_line="line before",
            start_line=10,
            end_line=20,
            next_context_line="line after"
        )
        assert context.source_id == 1
        assert context.start_line == 10
        assert context.end_line == 20

    def test_contextinfo_fields(self):
        """Test ContextInfo has correct fields."""
        fields = common.ContextInfo._fields
        expected = ('source_id', 'prev_context_line', 'start_line',
                   'end_line', 'next_context_line')
        assert fields == expected


class TestRegularExpressions:
    """Test regex patterns for comment detection."""

    def test_c_regex_exists(self):
        """Test C-style comment regex is defined."""
        assert hasattr(common, 'C_REGEX')
        assert common.C_REGEX is not None

    def test_python_regex_exists(self):
        """Test Python comment regex is defined."""
        assert hasattr(common, 'PY_REGEX')
        assert common.PY_REGEX is not None

    def test_shell_script_regex_exists(self):
        """Test Shell script comment regex is defined."""
        assert hasattr(common, 'SHELLSCRIPT_REGEX')
        assert common.SHELLSCRIPT_REGEX is not None

    def test_javascript_regex_exists(self):
        """Test JavaScript comment regex is defined."""
        assert hasattr(common, 'JS_REGEX')
        assert common.JS_REGEX is not None

    def test_whitespace_regex_matches_spaces(self):
        """Test WHITESPACE_REGEX matches spaces."""
        result = common.WHITESPACE_REGEX.sub('', 'a   b')
        assert result == 'ab'

    def test_whitespace_regex_matches_tabs(self):
        """Test WHITESPACE_REGEX matches tabs."""
        result = common.WHITESPACE_REGEX.sub('', 'a\t\tb')
        assert result == 'ab'

    def test_whitespace_regex_preserves_newlines(self):
        """Test WHITESPACE_REGEX preserves newlines."""
        result = common.WHITESPACE_REGEX.sub('', 'a b\nc d')
        assert '\n' in result


class TestHTMLEscapeDict:
    """Test HTML escape character mapping."""

    def test_html_escape_dict_is_dict(self):
        """Test HTML_ESCAPE_DICT is a dictionary."""
        assert isinstance(common.HTML_ESCAPE_DICT, dict)

    def test_html_escape_ampersand(self):
        """Test ampersand escape mapping."""
        assert common.HTML_ESCAPE_DICT['&'] == '&amp;'

    def test_html_escape_less_than(self):
        """Test less-than escape mapping."""
        assert common.HTML_ESCAPE_DICT['<'] == '&lt;'

    def test_html_escape_greater_than(self):
        """Test greater-than escape mapping."""
        assert common.HTML_ESCAPE_DICT['>'] == '&gt;'

    def test_html_escape_quote(self):
        """Test double quote escape mapping."""
        assert common.HTML_ESCAPE_DICT['"'] == '&quot;'

    def test_html_escape_apostrophe(self):
        """Test apostrophe escape mapping."""
        assert common.HTML_ESCAPE_DICT['\''] == '&apos;'


class TestVerbosePrint:
    """Test verbose_print utility function."""

    def test_verbose_print_function_exists(self):
        """Test verbose_print function exists."""
        assert hasattr(common, 'verbose_print')
        assert callable(common.verbose_print)

    def test_verbose_print_accepts_string(self):
        """Test verbose_print accepts string argument."""
        # Should not raise exception
        common.verbose_print("test message")

    def test_verbose_print_with_empty_string(self):
        """Test verbose_print handles empty string."""
        common.verbose_print("")
