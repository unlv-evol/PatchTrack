import argparse
from dataprep import load
import sys,os
import platform,subprocess

if __name__ == '__main__':
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
                        action='store', dest='context_line', type=int, default=10, metavar='NUM',\
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
        parser.print_help(sys.stderr)  # or sys.stdout
        sys.exit(1)

    args = parser.parse_args()

    #1. Install dependencies, create all the required directories and load data
    if(args.init):
        print("Installing OS specific dependencies................")
        try:
            if platform.system() == 'Darwin':
                subprocess.run(['brew', 'install', 'libmagic'])
            if platform.system() == 'Linux':
                subprocess.run(['apt', 'install', 'libmagic-dev'])
            if platform.system() == 'Windows':
                subprocess.run(['apt', 'install', 'libmagic-dev'])
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1)
        print("Installing Patch Track dependencies................")
        try:
            subprocess.run(['pip', 'install', 'pip', '--upgrade'])
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1);
        
        print("Setting up jupyter notebook................")
        try:
            subprocess.run(['ipython', 'kernel', 'install', '--user', '--name=venv'])
            subprocess.run(['python', '-m', 'ipykernel', 'install', '--user', '--name=venv'])
        except Exception as e:
            print("Error...: ", e)
            sys.exit(1);
        
        print("Extracting DevChatGPT and extended datasets................")
        load.extract_zip('dataprep/allPullRequestSharings.zip', 'data/extracted')
        print("Extracting ChatGPT and pull request patches................")
        load.extract_zip('dataprep/patches.zip', 'data/patches')
        
        # create directory to keep classified pickle files
        print("Setting up directory for storing classification file")
        if not os.path.exists('data/classified'):
            os.mkdir('data/classified')

        print("Complete successfully..........")
        print("You can now run 'python PatchTrack.py -r 1' to get the classification results!")
