"""Pytest configuration and shared fixtures for analyzer tests."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_patch_file(temp_dir):
    """Create a sample unified diff patch file for testing."""
    patch_content = """--- a/example.py
+++ b/example.py
@@ -10,6 +10,8 @@
 def hello():
-    print("old")
+    print("new")
     return True
 
@@ -20,3 +22,5 @@
     x = 5
+    y = 10
+    z = 15
"""
    patch_path = os.path.join(temp_dir, "test.patch")
    with open(patch_path, "w") as f:
        f.write(patch_content)
    return patch_path


@pytest.fixture
def sample_source_file(temp_dir):
    """Create a sample source code file for testing."""
    source_content = """# Sample Python source code
def hello():
    # Print message
    print("new")
    return True

def world():
    x = 5
    y = 10
    z = 15
"""
    source_path = os.path.join(temp_dir, "example.py")
    with open(source_path, "w") as f:
        f.write(source_content)
    return source_path


@pytest.fixture
def sample_patch_directory(temp_dir):
    """Create a directory with multiple patch files."""
    patch_dir = os.path.join(temp_dir, "patches")
    os.makedirs(patch_dir, exist_ok=True)
    
    # Create multiple patch files
    for i in range(3):
        patch_content = f"""--- a/file{i}.py
+++ b/file{i}.py
@@ -1,5 +1,6 @@
 def func{i}():
     x = {i}
-    return x
+    return x * 2
+    return x * 3
"""
        patch_path = os.path.join(patch_dir, f"patch{i}.patch")
        with open(patch_path, "w") as f:
            f.write(patch_content)
    
    return patch_dir


@pytest.fixture
def sample_source_directory(temp_dir):
    """Create a directory with multiple source files."""
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    
    # Create multiple source files
    for i in range(3):
        source_content = f"""# Source file {i}
def func{i}():
    x = {i}
    return x * 2
"""
        src_path = os.path.join(src_dir, f"file{i}.py")
        with open(src_path, "w") as f:
            f.write(source_content)
    
    return src_dir
