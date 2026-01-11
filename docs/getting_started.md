# Getting Started with PatchTrack

!!! info "Python Version"
    PatchTrack requires **Python >= 3.10**. Please verify your Python version before proceeding.

## Quick Start

Get PatchTrack up and running in just 3 steps:

```bash
# 1. Clone the repository
git clone https://github.com/replication-pack/PatchTrack.git
cd PatchTrack

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Initialize PatchTrack (installs dependencies & datasets)
python PatchTrack.py --init
```

That's it! You can now start using PatchTrack. Proceed to [Running the Tool](#running-the-tool) section.

---

## System Requirements

### Minimum Specifications
- **Operating System**: macOS, Linux, or Windows
- **Python**: >= 3.10
- **RAM**: >= 4 GB
- **Storage**: >= 1 GB
- **Processor**: CPU 1.18 GHz or greater
- **Git**: Latest version

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/replication-pack/PatchTrack.git
cd PatchTrack
```

### Step 2: Create Python Virtual Environment

=== "macOS & Linux"

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

=== "Windows"

    ```powershell
    python -m venv venv
    venv\Scripts\activate
    ```

### Step 3: Install Dependencies

PatchTrack has two types of dependencies:

1. **OS-specific**: `libmagic` library (required before Python dependencies)
2. **Python packages**: Automatically installed in the next step

#### Install OS Dependencies

=== "macOS"

    ```bash
    # Using Homebrew
    brew install libmagic
    ```

=== "Ubuntu/Debian"

    ```bash
    sudo apt-get update
    sudo apt-get install libmagic1
    ```

=== "Fedora/RHEL"

    ```bash
    sudo dnf install file-libs
    ```

=== "Windows"

    Windows users can skip this step - `libmagic` is handled by Python packages.

!!! note "Alternative: Automated Script"
    You can also run the automated installation script:
    ```bash
    cd bin/
    chmod +x os-package.sh
    ./os-package.sh
    ```
    This script automatically detects your OS and installs the appropriate dependencies.

### Step 4: Initialize PatchTrack

This command installs all Python dependencies and extracts datasets:

```bash
python PatchTrack.py --init
```

!!! success "Installation Complete!"
    Your PatchTrack environment is ready to use.

---

## Verify Installation

Confirm everything is set up correctly by running the verification script:

```bash
python -c "import pandas; import requests; print('✅ All dependencies installed successfully!')"
```

You should also see a `data/` directory with extracted datasets.

---

## Project Structure

<details>
<summary><b>Click to expand directory structure</b></summary>

```
.
├── LICENSE                     # MIT License
├── PatchTrack.py               # Main entry point
├── README.md                   # Project README
├── requirements.txt            # Python dependencies
├── mkdocs.yml                  # Documentation config
│
├── analyzer/                   # Core analysis modules
│   ├── __init__.py
│   ├── main.py                 # Main PatchTrack class
│   ├── classifier.py           # Patch classification (PA/PN/NE)
│   ├── patchLoader.py          # Parse PR patches (diff format)
│   ├── sourceLoader.py         # Parse ChatGPT code snippets
│   ├── analysis.py             # Result visualization & plotting
│   ├── aggregator.py           # Aggregate PR-level decisions
│   ├── helpers.py              # Utility functions (API, normalization)
│   ├── common.py               # Shared settings (n-grams, file types)
│   ├── constant.py             # Global constants
│   └── dataDict.py             # Track PR-project pair info
│
├── dataprep/                   # Data preparation
│   ├── __init__.py
│   ├── load.py                 # Dataset loading functions
│   ├── allPullRequestSharings.zip  # Main dataset
│   ├── patches.zip             # Extracted patches
│   └── manual/                 # Custom dataset generation docs
│
├── notebooks/                  # Jupyter experiments
│   ├── __init__.py
│   └── run_experiment.ipynb    # Reproduce paper results
│
├── bin/                        # Installation scripts
│   └── os-package.sh           # OS-specific dependency installer
│
├── docs/                       # Documentation
│   ├── index.md
│   ├── getting_started.md
│   └── reference/
│
├── output/                     # Results & visualizations
├── tests/                      # Unit tests (WIP)
├── RQ1_2_3_4/                  # Research question results
│
└── tokens-example.txt          # GitHub tokens template
```

</details>

---

## Running PatchTrack

### Option 1: Jupyter Notebook (Recommended)

The **easiest way** to test and reproduce the paper results:

```bash
# Make sure your virtual environment is activated
cd notebooks/
jupyter notebook run_experiment.ipynb
```

!!! success "Recommended for:"
    - Reproducing published results
    - Interactive exploration
    - Learning how PatchTrack works

### Option 2: Command Line

Use PatchTrack with customizable command-line arguments:

```bash
python PatchTrack.py [OPTIONS]
```

---

## Command Reference

| Command | Description | Default |
|---------|-------------|---------|
| `-h, --help` | Show help message | - |
| `-i, --init` | Setup datasets & directories (run once) | - |
| `-n, --ngram NUM` | N-gram size in lines | 1 |
| `-c, --context NUM` | Context lines for output | 10 |
| `-v, --verbose` | Enable verbose logging | False |
| `-p, --patch_path STR` | Path to ChatGPT/PR patches | `data/patches` |
| `-s, --source_path STR` | Path to extracted conversations | `data/extracted` |
| `-r, --restore` | Restore default settings & directories | - |

### Example Usage

```bash
# Run with custom n-gram size and verbose output
python PatchTrack.py -n 4 -v

# Use custom patch directory
python PatchTrack.py -p /path/to/patches

# Restore defaults
python PatchTrack.py -r
```

For detailed help:

```bash
python PatchTrack.py --help
```

---

## GitHub Tokens Configuration

### Why GitHub Tokens?

GitHub API has rate limits. Using authentication tokens increases your rate limit from **60 to 5,000 requests per hour**, which is essential for processing many PRs.

### Setup Instructions

1. **Create tokens** at [GitHub Settings → Tokens (classic)](https://github.com/settings/tokens)
   - Select these scopes: `public_repo`, `read:user`
   - Save your tokens in a secure location

2. **Configure PatchTrack** with your tokens:
   - Copy `tokens-example.txt` to `tokens.txt`
   - Add your tokens (comma-separated):

   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxx,ghp_yyyyyyyyyyyyyyyyyyyyy,ghp_zzzzzzzzzzzzzzzzzzzz
   ```

!!! warning "Security Note"
    - **Never commit** `tokens.txt` to version control
    - Use **multiple tokens** (minimum 2 recommended) to avoid rate limit issues
    - Rotate tokens regularly
    - Keep tokens private and secure

### Rate Limiting

With rotating tokens, PatchTrack can process:
- ~500 PRs per token without hitting rate limits
- Multiple tokens provide redundancy and higher throughput

---

## Troubleshooting

### libmagic Not Found

**Error:** `ImportError: libmagic not found`

**Solution:** Install libmagic using the OS-specific method above, or run:

```bash
cd bin/
chmod +x os-package.sh
./os-package.sh
```

### ModuleNotFoundError: No module named 'X'

**Error:** Missing Python dependencies

**Solutions:**
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run initialization again:
   ```bash
   python PatchTrack.py --init
   ```

### Permission Denied (macOS/Linux)

**Error:** `PermissionError: [Errno 13]`

**Solution:** Ensure you have read/write permissions to the directory and activate your virtual environment.

### Python Version Mismatch

**Error:** `SyntaxError` or version-related issues

**Solution:** Verify Python version:
```bash
python --version  # Should show Python 3.10 or higher
```

If needed, use `python3.10` or `python3.11` instead of `python`.

### GitHub API Rate Limit

**Error:** `HTTP 403: API rate limit exceeded`

**Solutions:**
1. Add more tokens to `tokens.txt`
2. Increase token count and restart
3. Wait for rate limit to reset (typically 1 hour)

### Jupyter Notebook Issues

**Error:** `No module named 'jupyter'`

**Solution:**
```bash
pip install jupyter notebook
```

Then restart the notebook kernel.

---

## Next Steps

- **Explore Results**: Check the `notebooks/run_experiment.ipynb` for data analysis
- **View Output**: Results are saved in the `output/` directory
- **Research Questions**: See `RQ1_2_3_4/` for detailed findings
- **Customize**: Modify command-line arguments to analyze different datasets

---

## Need Help?

- 📖 See the [Reference Documentation](../reference/common.md)
- 🐛 Report issues on [GitHub](https://github.com/replication-pack/PatchTrack/issues)
- 💬 Check the [README](../README.md) for more details
