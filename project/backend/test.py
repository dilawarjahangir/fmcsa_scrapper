import os

# Determine the base directory (the directory where this script resides)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILENAME = 'allcode.py'
output_file_path = os.path.join(BASE_DIR, OUTPUT_FILENAME)

def gather_py_files(dir_path, output_file):
    """
    Recursively reads a directory and appends contents of each .py file to output_file.
    
    Args:
        dir_path (str): The directory to read from.
        output_file (file object): Opened file object for writing the combined output.
    """
    # Walk through the directory tree
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # Only process .py files, and skip the output file itself
            if file.endswith('.py') and file != OUTPUT_FILENAME:
                full_path = os.path.join(root, file)
                # Get the file path relative to BASE_DIR for commenting
                relative_path = os.path.relpath(full_path, BASE_DIR)
                output_file.write(f"\n# {relative_path}:\n\n")
                with open(full_path, 'r', encoding='utf-8') as f:
                    output_file.write(f.read())
                output_file.write("\n")

def main():
    # If 'allcode.py' exists, remove it to start fresh
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    
    # Open the output file in append mode
    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        gather_py_files(BASE_DIR, output_file)
    
    print(f"All .py files have been combined into \"{OUTPUT_FILENAME}\"")

if __name__ == '__main__':
    main()
