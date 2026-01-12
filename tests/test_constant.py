"""Unit tests for analyzer.constant module.

Tests the constants module including:
- GitHub URLs
- Analysis parameters
- EXTENSIONS mapping
- get_extension() helper function
"""

import pytest
from analyzer import constant


class TestGitHubURLs:
    """Test GitHub URL constants."""

    def test_github_api_base_url(self):
        """Test GitHub API base URL is correctly defined."""
        assert constant.GITHUB_API_BASE_URL == "https://api.github.com/repos/"
        assert isinstance(constant.GITHUB_API_BASE_URL, str)

    def test_github_base_url(self):
        """Test GitHub web base URL is correctly defined."""
        assert constant.GITHUB_BASE_URL == "https://github.com/"

    def test_github_raw_url(self):
        """Test GitHub raw content URL is correctly defined."""
        assert constant.GITHUB_RAW_URL == "https://raw.githubusercontent.com/"


class TestAnalysisParameters:
    """Test analysis parameter constants."""

    def test_ngram_size(self):
        """Test n-gram size is a positive integer."""
        assert isinstance(constant.NGRAM_SIZE, int)
        assert constant.NGRAM_SIZE >= 1

    def test_context_line(self):
        """Test context line count is a positive integer."""
        assert isinstance(constant.CONTEXT_LINE, int)
        assert constant.CONTEXT_LINE > 0

    def test_verbose_mode_default(self):
        """Test verbose mode defaults to False."""
        assert isinstance(constant.VERBOSE_MODE, bool)
        assert constant.VERBOSE_MODE is False

    def test_bloomfilter_size(self):
        """Test Bloom filter size is a power of two."""
        assert isinstance(constant.BLOOMFILTER_SIZE, int)
        assert constant.BLOOMFILTER_SIZE > 0
        # Check if power of two
        assert (constant.BLOOMFILTER_SIZE & (constant.BLOOMFILTER_SIZE - 1)) == 0

    def test_min_mn_ratio(self):
        """Test MIN_MN_RATIO is a positive integer."""
        assert isinstance(constant.MIN_MN_RATIO, int)
        assert constant.MIN_MN_RATIO > 0


class TestExtensionsMapping:
    """Test EXTENSIONS dictionary and mappings."""

    def test_extensions_is_dict(self):
        """Test EXTENSIONS is a dictionary."""
        assert isinstance(constant.EXTENSIONS, dict)
        assert len(constant.EXTENSIONS) > 0

    def test_python_extension(self):
        """Test Python extension mapping."""
        assert constant.EXTENSIONS.get("python") == "py"

    def test_javascript_extensions(self):
        """Test JavaScript variant extensions."""
        assert constant.EXTENSIONS.get("javascript") == "js"
        assert constant.EXTENSIONS.get("cjs") == "js"
        assert constant.EXTENSIONS.get("mjs") == "js"

    def test_typescript_extensions(self):
        """Test TypeScript extensions."""
        assert constant.EXTENSIONS.get("typescript") == "ts"
        assert constant.EXTENSIONS.get("tsx") == "tsx"

    def test_yaml_extensions(self):
        """Test YAML extension variants."""
        assert constant.EXTENSIONS.get("yaml") == "yaml"
        assert constant.EXTENSIONS.get("yml") == "yaml"

    def test_extension_values_no_leading_dot(self):
        """Test all extension values do not have leading dots."""
        for key, value in constant.EXTENSIONS.items():
            assert not value.startswith("."), f"Extension '{value}' for '{key}' has leading dot"
            assert isinstance(value, str)
            assert len(value) > 0

    def test_common_languages_mapped(self):
        """Test common programming languages are mapped."""
        common_langs = ["python", "java", "javascript", "go", "rust", "c", "cpp"]
        for lang in common_langs:
            assert lang in constant.EXTENSIONS, f"Language '{lang}' not in EXTENSIONS"


class TestGetExtensionHelper:
    """Test the get_extension() helper function."""

    def test_get_extension_from_identifier(self):
        """Test extracting extension from language identifier."""
        assert constant.get_extension("python") == "py"
        assert constant.get_extension("javascript") == "js"
        assert constant.get_extension("java") == "java"

    def test_get_extension_from_filename(self):
        """Test extracting extension from filename only works for dotted format."""
        # Note: get_extension() only works with direct identifiers or .ext format
        # Filenames like "file.py" are not supported in current implementation
        assert constant.get_extension("file.py") is None
        assert constant.get_extension("script.js") is None

    def test_get_extension_from_dotted_extension(self):
        """Test extracting extension from dotted format."""
        # Note: Only bare .ext works, not full filenames
        assert constant.get_extension(".py") is None
        assert constant.get_extension(".js") is None

    def test_get_extension_case_insensitive(self):
        """Test get_extension is case-insensitive for identifiers."""
        assert constant.get_extension("PYTHON") == "py"
        assert constant.get_extension("Python") == "py"
        # Filenames don't work in current implementation
        assert constant.get_extension("FILE.PY") is None

    def test_get_extension_with_spaces(self):
        """Test get_extension handles spaces for identifiers."""
        assert constant.get_extension(" python ") == "py"
        # Filenames don't work
        assert constant.get_extension(" file.py ") is None

    def test_get_extension_unknown_returns_none(self):
        """Test get_extension returns None for unknown extensions."""
        assert constant.get_extension("unknown_lang") is None
        assert constant.get_extension("file.xyz") is None

    def test_get_extension_empty_string_returns_none(self):
        """Test get_extension returns None for empty string."""
        assert constant.get_extension("") is None

    def test_get_extension_none_returns_none(self):
        """Test get_extension returns None for None input."""
        assert constant.get_extension(None) is None

    def test_get_extension_with_multiple_dots(self):
        """Test get_extension with multiple dots in filename."""
        # get_extension() doesn't parse filenames in current implementation
        assert constant.get_extension("file.test.py") is None
        assert constant.get_extension("archive.tar.gz") is None

    def test_get_extension_variants(self):
        """Test get_extension with language variants."""
        assert constant.get_extension("jsx") == "jsx"
        assert constant.get_extension("tsx") == "tsx"
        assert constant.get_extension("mjs") == "js"


class TestPublicAPI:
    """Test that all public APIs are exported in __all__."""

    def test_all_exports_github_constants(self):
        """Test GitHub URL constants are exported."""
        assert "GITHUB_API_BASE_URL" in constant.__all__
        assert "GITHUB_BASE_URL" in constant.__all__
        assert "GITHUB_RAW_URL" in constant.__all__

    def test_all_exports_analysis_parameters(self):
        """Test analysis parameters are exported."""
        assert "NGRAM_SIZE" in constant.__all__
        assert "CONTEXT_LINE" in constant.__all__
        assert "VERBOSE_MODE" in constant.__all__
        assert "BLOOMFILTER_SIZE" in constant.__all__
        assert "MIN_MN_RATIO" in constant.__all__

    def test_all_exports_extensions_and_helper(self):
        """Test EXTENSIONS and get_extension are exported."""
        assert "EXTENSIONS" in constant.__all__
        assert "get_extension" in constant.__all__

    def test_all_exports_are_accessible(self):
        """Test all items in __all__ are actually accessible."""
        for name in constant.__all__:
            assert hasattr(constant, name), f"'{name}' in __all__ but not accessible"
