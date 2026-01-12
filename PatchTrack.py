import argparse
from dataprep import load
import sys
import os
import platform
import subprocess


def install_os_dependencies() -> None:
    """Install OS-specific system dependencies (best-effort).

    This preserves the original mapping of commands per platform.
    """
    install_cmds = {
        'Darwin': ['brew', 'install', 'libmagic'],
        'Linux': ['apt', 'install', 'libmagic-dev'],
        'Windows': ['apt', 'install', 'libmagic-dev'],
    }
    cmd = install_cmds.get(platform.system())
    if cmd:
        subprocess.run(cmd)


def install_python_dependencies() -> None:
    """Install Python-side dependencies via pip (best-effort)."""
    subprocess.run(['pip', 'install', 'pip', '--upgrade'])
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])


def setup_jupyter_kernel() -> None:
    """Install a local IPython kernel named 'venv' (best-effort)."""
    subprocess.run(['ipython', 'kernel', 'install', '--user', '--name=venv'])
    subprocess.run(['python', '-m', 'ipykernel', 'install', '--user', '--name=venv'])


def extract_datasets() -> None:
    """Extract packaged data archives into data directories."""
    load.extract_zip('dataprep/allPullRequestSharings.zip', 'data/extracted')
    load.extract_zip('dataprep/patches.zip', 'data/patches')


def ensure_classified_dir() -> None:
    os.makedirs('data/classified', exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    # optional arguments
    parser.add_argument('-i', '--init',
                        action='store_true',
                        dest='init',
                        help='setup required datasets and directories. This command should be executed at least once')
    parser.add_argument('-n', '--ngram',
                        action='store',
                        dest='ngram_size',
                        type=int,
                        default=1,
                        metavar='NUM',
                        help='use n-gram of NUM lines (default: %(default)s)')
    parser.add_argument('-c', '--context',
                        action='store', dest='context_line', type=int, default=10, metavar='NUM',
            help='print NUM lines of context (default: %(default)s)')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose_mode',
                        default=False,
                        help='enable verbose mode (default: %(default)s)')
    parser.add_argument('-p', '--patch_path',
                        action='store',
                        default='data/patches',
                        metavar='STR',
                        help='path to ChatGPT and PR patch files (default: %(default)s)')
    parser.add_argument('-s', '--source_path',
                        action='store',
                        default='data/extracted',
                        help='path to json files of extracted ChatGPT conversations and code snippets (default: %(default)s)')
    parser.add_argument('-r', '--restore',
                        action='store_true',
                        dest='teardown',
                        help='restore default setting, files and directories')

    # Check if no arguments were provided, and if so, print the help message
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # 1. Install dependencies, create required directories and load data
    if args.init:
        print("Installing OS specific dependencies................")
        try:
            install_os_dependencies()
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)

        print("Installing Patch Track dependencies................")
        try:
            install_python_dependencies()
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)

        print("Setting up jupyter notebook................")
        try:
            setup_jupyter_kernel()
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)

        print("Extracting DevChatGPT and extended datasets................")
        try:
            extract_datasets()
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)

        # create directory to keep classified pickle files
        print("Setting up directory for storing classification file")
        try:
            ensure_classified_dir()
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)

        print("Complete successfully..........")
        print("You can now run 'python PatchTrack.py -r 1' to get the classification results!")


if __name__ == '__main__':
    main()
