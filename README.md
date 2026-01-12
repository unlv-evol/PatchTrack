# PatchTrack: A Comprehensive Analysis of ChatGPT’s Influence on Pull Request Outcomes

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14978624.svg)](https://doi.org/10.5281/zenodo.14978624)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/unlv-evol/PatchTrack/main)
![GitHub License](https://img.shields.io/github/license/unlv-evol/PatchTrack)
[![Docs deployment](https://github.com/unlv-evol/PatchTrack/actions/workflows/doc-deploy.yaml/badge.svg)](https://github.com/unlv-evol/PatchTrack/actions/workflows/doc-deploy.yaml)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B46484%2Fgithub.com%2Funlv-evol%2FPatchTrack.svg?type=shield&issueType=license)](https://app.fossa.com/projects/custom%2B46484%2Fgithub.com%2Funlv-evol%2FPatchTrack?ref=badge_shield&issueType=license)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B46484%2Fgithub.com%2Funlv-evol%2FPatchTrack.svg?type=shield&issueType=security)](https://app.fossa.com/projects/custom%2B46484%2Fgithub.com%2Funlv-evol%2FPatchTrack?ref=badge_shield&issueType=security)


### Abstract (Short)

The rapid adoption of **large language models (LLMs)** like ChatGPT has introduced new dynamics in software development, particularly within pull request workflows. While prior research has examined the quality of AI-generated code, little is known about how developers actually use these suggestions in real-world collaboration. We analyze **338 pull requests** from **255** GitHub repositories containing self-admitted ChatGPT usage, including **645** AI-generated snippets and **3,486** developer-authored patches. We introduce `PatchTrack`, a tool that classifies whether ChatGPT patches were applied, not applied, or not suggested, enabling fine-grained analysis of AI-assisted decisions. Full adoption of ChatGPT code is rare: the median integration rate was **25%**. A qualitative analysis of **89** pull requests with integrated patches revealed recurring patterns of *structural integration*, *selective extraction*, and *iterative refinement*, showing that developers typically treat ChatGPT’s output as a starting point rather than a final implementation.

## Directory Structure and Description
```
.
├── LICENSE                     # The License for the tool - MIT License
├── PatchTrack.py               # Main entrypoint of the tool
├── README.md                   # Readme file to describe how the tool work
├── RQ1_2_3_4                   # Contains all the results for RQ1, RQ2, RQ3 and RQ4
├── analyzer                    # Directory for core modules of the tool   
│   ├── __init__.py
│   ├── analysis.py             # Plotting the classification result
│   ├── classifier.py           # Classifies the dataset as PA, PN or NE
│   ├── common.py               # Setting n-grams, file types, etc
│   ├── constant.py             # All the constant variables used in the tool   
│   ├── dataDict.py             # Keep track of extracted pr-project-pair information 
│   ├── helpers.py              # All helper functions e.g. api requests, normalization, etc.
│   ├── main.py                 # Main PatchTrack class
│   ├── patchLoader.py          # Parse and tokenize PR patches. The file should be a diff format
│   ├── sourceLoader.py         # Parse and tokenize ChatGPT code snippet
│   └── totals.py               # Compute total number of PA, PN or NE classified
├── bin                         
│   └── os-packages.sh          # OS-specific dependencies 
├── dataprep                    
│   ├── __init__.py
│   ├── allPullRequestSharings.zip    # DevGPT and Extended json dataset   
│   ├── load.py                       # Functions for loading datasets
│   ├── manual                        # Procedures on how to generate the extended dataset
│   └── patches.zip                   # Extracted ChatGPT code snippest and PR patches
├── notebooks                    # Notebooks containing code for running the experiments
│   ├── __init__.py
│   └── run_experiment.ipynb
├── output                       # figures and csv files of all the results of running the tool
├── requirements.txt             # List of python dependencies required by the tool
├── tests                        # Testing different component of the tool. This is still a WIP
└── tokens-example.txt           # Example file containing GitHub API tokens seperated by a comma (,). This should be renamed to `tokens.txt`
```

## Setting up 
To setup and test `PatchTrack` tool on your local computer, follow the steps below:
### Get the code
The easiest way is using the `git clone` command:

```bash
git clone https://github.com/replication-pack/PatchTrack.git
```
### Minimum System Requirements
- `Operating System`: Mac0SX, Linux, Windows
- `RAM`: >= 4 GB
- `Storage`: >= 1 GB
- `Processor`: CPU 1.18 GHz or greater
#### Other tools
- Git, Python >= 3.10
### Python Virtual Environment
Let's set python virtual environment;

```bash
cd PatchTrack/

python3 -m venv venv
```
Activate the virtual environment 

```bash
source venv/bin/activate
```
### Dependencies and Dataset

`PatchTrack` consist of two categories of depencies i.e. (i) OS specific dependencies and (ii) development dependencies. The OS specific dependency is `libmagic`. To dependencis will be installed automatically when you start the tool.  

Datasets are stored in the `dataprep` directory in zipped files. This will be automatically extracted and placed in the right directory using the step below. Now, let us install the dependencies and load the required datasets.

```bash
python PatchTrack.py --init
```
The above command will install all the required packages, set directories and unzip datasets for the smooth execution of the tool.
Note: `PatchTrack` has been tested on `python >= 3.10`

You can also install the OS-specific libraries manually on `Ubuntu/Debian` or `MacOS X`, by runing the shell script in the `bin` directory.

```bash
cd bin/
chmod +x os-package.sh
./os-package.sh
```
The above code will automatically detect the OS (Linux or MacOS X) and install the libraries. Note: This is required before installing development specific dependencies.

## Running the tool
### Notebook - Reproducing the results
This is the easiest approach to test the tool and **reproduce the classification results presented in the paper**. In the `notebooks` directory, simply run the `run_experiment.ipynb` file. 
### Console
If you wish to play with `PatchTrack`, there are a number of command line arguments for configuring different part of the tool. Some of those option are actively being improved. We are developing a comprehensive documentation of the tool which will be uploaded soon.
### List of Commands
Information of the other command line options are provided by using `-h` or `--help`
```
usage: PatchTrack.py [-h] [-i] [-n NUM] [-c NUM] [-v] [-p STR] [-s SOURCE_PATH] [-r]

options:
  -h, --help            show this help message and exit
  -i, --init            setup required datasets and directories. This command should be executed at least once
  -n NUM, --ngram NUM   use n-gram of NUM lines (default: 1)
  -c NUM, --context NUM
                        print NUM lines of context (default: 10)
  -v, --verbose         enable verbose mode (default: False)
  -p STR, --patch_path STR
                        path to ChatGPT and PR patch files (default: data/patches)
  -s SOURCE_PATH, --source_path SOURCE_PATH
                        path to json files of extracted ChatGPT conversations and code snippets (default: data/extracted)
  -r, --restore         restore default setting, files and directories
```
### GitHub Tokens
We use [GitHub tokens](https://github.com/settings/tokens) when extracting PR patches. This allows for higher rate limit because of the high number of requests to the GitHub API. Tokens can be set in the `tokens.txt` file seperated by a comman. The user can add as many tokens as needed. A minimal of 2 tokens can be used to safely execute code and to make sure that the rate limit is not reached for a token.
## License
This repository is MIT licensed. See the [LICENSE](./LICENSE) file for more information.
