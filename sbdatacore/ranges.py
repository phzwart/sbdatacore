import os
import re
from collections import defaultdict

def range_parser(txt):
    """
    Parses a text string into a list of ranges.

    Args:
    txt (str): A text string containing ranges, e.g., "1-3,5".

    Returns:
    list: A list of lists, where each sublist represents a range.
    """
    splitter = " "
    if "," in txt:
        splitter = ","
    txt_ranges = txt.split(splitter)
    ranges = []
    for range_ in txt_ranges:
        tmp = range_.split("-")
        assert len(tmp) <= 2
        if len(tmp) == 2:
            ranges.append([int(tmp[0]), int(tmp[1])])
        if len(tmp) == 1:
            ranges.append([int(tmp[0])])
    return ranges

def range_to_list(range_):
    """
    Converts a range list into a list of numbers.

    Args:
    range_ (list): A list of range lists.

    Returns:
    list: A list of integers representing the range.
    """
    result = []
    for item in range_:
        if len(item) == 1:
            result.append(item[0])
        if len(item) == 2:
            result.extend(range(item[0], item[1] + 1))
    return result

class SerialFileNameHandler(object):
    """
    A class to handle serialized file names based on a user-defined base name and wildcard.
    """
    def __init__(self, base_name, wildcard="#"):
        """
        Initializes the SerialFileNameHandler object.

        Args:
        base_name (str): The base name of the file.
        wildcard (str): The wildcard character used in the file name.
        """
        self.user_base_name = base_name
        self.wildcard = wildcard
        self.base, self.extension, self.n = self.process_user_input()

    def process_user_input(self):
        """
        Processes the user input to extract the base name, extension, and wildcard count.

        Returns:
        tuple: A tuple containing the base name, extension, and number of wildcards.
        """
        at_serial = False
        at_extension = False
        p1 = ""
        p3 = ""
        n = 0

        for ii in self.user_base_name:
            if ii == self.wildcard and not at_extension:
                at_serial = True
                n += 1
                continue
            if at_serial and ii != self.wildcard:
                at_extension = True
            if at_extension:
                p3 += ii
            else:
                p1 += ii

        # Correcting the logic for base and extension separation
        return p1, p3, n

    def name_from_number(self, serial_id=1):
        """
        Generates a file name from a serial number.

        Args:
        serial_id (int): The serial number to generate the file name.

        Returns:
        str: The generated file name.
        """
        id_str = str(serial_id)
        return self.base + (self.n - len(id_str)) * "0" + id_str + self.extension

    def names_from_range_list(self, range_list):
        """
        Generates file names from a list of ranges.

        Args:
        range_list (list): A list of ranges.

        Returns:
        list: A list of generated file names.
        """
        result = []
        for id in range_list:
            result.append(self.name_from_number(id))
        return result

    def names_from_range(self, range_txt):
        """
        Generates file names from a range text.

        Args:
        range_txt (str): A text string representing ranges.

        Returns:
        list: A list of generated file names.
        """
        range_list = range_to_list(range_parser(range_txt))
        return self.names_from_range_list(range_list)

def parse_file_names(file_names):
    """
    Parses a list of file names and generates a range string for the numeric parts.

    Args:
    file_names (list): A list of file names in a specific format.

    Returns:
    tuple: A tuple containing the base name with wildcard and the range string.
    """
    if not file_names:
        return None, None

    numeric_parts = []
    base_name_pattern = None
    use_extended_wildcard = False  # Flag to determine if extended wildcards are needed

    for file in file_names:
        # Extract the numeric part and the rest of the file name
        match = re.search(r'(\d+)(\.[^.]+)$', file)
        if match:
            numeric_part = match.group(1)
            numeric_parts.append(int(numeric_part))

            if base_name_pattern is None:
                base_name_pattern = file.replace(numeric_part, "{}")
                # Check if leading zeros are present
                if numeric_part.startswith("0"):
                    use_extended_wildcard = True

        else:
            return None, None

    if base_name_pattern is None:
        return None, None

    # Replace {} with the appropriate number of wildcards
    wildcard = '#' * len(numeric_part) if use_extended_wildcard else '#'
    base_name_with_wildcard = base_name_pattern.format(wildcard)

    # Sort and group the numbers
    numeric_parts.sort()
    ranges = []
    start = end = numeric_parts[0]

    for n in numeric_parts[1:]:
        if n - end == 1:
            end = n
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = end = n
    ranges.append(f"{start}-{end}" if start != end else str(start))

    # Format ranges into a string
    range_str = ','.join(ranges)
    return base_name_with_wildcard, range_str

def group_files_by_pattern(file_names):
    """
    Groups files by their base name pattern, including wildcards.

    Args:
    file_names (list): A list of file names.

    Returns:
    dict: A dictionary grouping files by their base name pattern.
    """
    base_name_info = defaultdict(lambda: {"max_digits": 0, "files": [], "has_leading_zeros": False})

    for file in file_names:
        match = re.search(r'(\d+)(\.[^.]+)$', file)
        if match:
            numeric_part, extension = match.groups()
            base_name = file[:-len(numeric_part+extension)]
            max_digits = max(base_name_info[(base_name, extension)]["max_digits"], len(numeric_part))
            has_leading_zeros = base_name_info[(base_name, extension)]["has_leading_zeros"] or numeric_part.startswith("0")

            base_name_info[(base_name, extension)]["max_digits"] = max_digits
            base_name_info[(base_name, extension)]["files"].append(file)
            base_name_info[(base_name, extension)]["has_leading_zeros"] = has_leading_zeros
        else:
            base_name_info[None]["files"].append(file)  # Files that do not match the pattern

    grouped_files = {}
    for key, value in base_name_info.items():
        if key is None:
            # Handle the None key separately
            grouped_files[key] = value["files"]
        else:
            # Unpack the key into base_name and extension
            base_name, extension = key
            if value["has_leading_zeros"]:
                wildcard = '#' * value["max_digits"]
            else:
                wildcard = '#'
            wildcard_pattern = base_name + wildcard + extension
            grouped_files[wildcard_pattern] = value["files"]

    return grouped_files


def parse_file_list(file_names):
    """
    Parses a list of file names, groups them by pattern, and identifies non-sequential files.

    Args:
    file_names (list): A list of file names.

    Returns:
    tuple: A tuple containing a list of grouped file names with ranges and a list of non-sequential files.
    """
    # Group files by their base pattern
    grouped_files = group_files_by_pattern(file_names)

    # Parse each group of files and identify non-sequential files
    results = []
    non_sequential_files = grouped_files.pop(None, [])  # Extract files that didn't fit the pattern

    for base_name_with_wildcard, files in grouped_files.items():
        _, range_str = parse_file_names(files)
        if range_str:
            results.append((base_name_with_wildcard, range_str))
        else:
            non_sequential_files.extend(files)  # Add files that couldn't form a sequence

    return results, non_sequential_files
