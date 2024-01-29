import os
import ranges  # Ensure you have the 'ranges' module imported

def list_dirs_with_file_count(startpath):
    """
    Generates a visual tree structure representing the directory hierarchy starting from a given path.
    Each directory and subdirectory is listed with the count of files it contains. Files within
    each directory are processed and displayed, either individually or as a range if they follow
    a numerical sequence.

    The output is formatted with connectors (├── and └──) and indentation to reflect the hierarchy
    and relationship between directories and files. The function uses the 'ranges' module to
    summarize files with numerical sequences.

    Args:
    startpath (str): The root directory path from which the tree structure is generated.

    Example of output:
        root_dir/
        ├── subdir1/ (2 files)
        │   ├── file1.txt
        │   └── file2.txt
        └── subdir2/ (3 files)
            ├── file3.txt
            └── (file_#.jpg, 1-10)  # Summarized range of files

    Note:
    - The 'ranges' module must be correctly implemented and imported for the file range summary to work.
    - This function is recursive and may not be suitable for directories with extremely deep hierarchies.
    """

    tree = {}

    for root, dirs, files in os.walk(startpath):
        pointer = tree
        for part in root[len(startpath):].lstrip(os.sep).split(os.sep):
            pointer = pointer.setdefault(part, {})
        pointer['_files'] = files

    def build_tree_string(current_tree, prefix='', result=''):
        entries = list(current_tree.items())
        entries_count = len(entries)

        for i, (key, value) in enumerate(entries):
            if key == '_files':
                continue

            connector = '└── ' if i == entries_count - 1 else '├── '
            line = f"{prefix}{connector}{key}/ ({len(value.get('_files', []))} files)" if len(value.get('_files', [])) > 0 else f"{prefix}{connector}{key}/"
            result += line + '\n'

            if value.get('_files'):
                file_indent = prefix + ('    ' if i == entries_count - 1 else '│   ')
                s, o = ranges.parse_file_list(value['_files'])
                for f_s in s:
                    result += f"{file_indent}    {f_s}\n"
                for f_o in o:
                    result += f"{file_indent}    {f_o}\n"

            if isinstance(value, dict):
                ext = '    ' if i == entries_count - 1 else '│   '
                result = build_tree_string(value, prefix=prefix + ext, result=result)

        return result

    # Generate the tree string from the root
    return build_tree_string(tree)

if __name__ == "__main__":
    tree_string = list_dirs_with_file_count("./")
    print(tree_string)
