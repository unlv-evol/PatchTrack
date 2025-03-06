import zipfile
import os

def extract_zip(zip_path, extract_to):
    """
    Extracts a ZIP file to a specified folder.

    Args:
    zip_path (str): The path to the ZIP file.
    extract_to (str): The directory to extract the files to.

    Returns:
    None
    """
    # Ensure the target directory exists, if not, create it
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # Open the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all the contents into the directory
        zip_ref.extractall(extract_to)
    print(f"Files extracted to {extract_to}")