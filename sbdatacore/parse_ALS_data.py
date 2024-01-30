import os
import shutil
from sbdatacore import parse_udb, ranges, dates, permissions

import os


def count_files_in_subdirectories(directory):
    """
    Count the number of files in all subdirectories of a given directory.

    Args:
    directory (str): The directory in which to count files.

    Returns:
    int: The total number of files in all subdirectories.
    """
    file_count = 0
    # Walk through all subdirectories and files in the directory
    for root, dirs, files in os.walk(directory):
        # Add the number of files in the current directory to the total count
        file_count += len(files)

    return file_count


def remove_empty_subdirectories(directory):
    """
    Remove all empty subdirectories within a given directory.

    Args:
    directory (str): The root directory from which to remove empty subdirectories.
    """
    # Walk through the directory tree, top-down, so we don't try to
    # remove a directory before we have removed its subdirectories
    for root, dirs, files in os.walk(directory, topdown=False):
        for this_dir in dirs:
            # Construct the full path to the subdirectory
            full_dir_path = os.path.join(root, this_dir)

            # Check if the subdirectory is empty
            if not os.listdir(full_dir_path):
                # Remove the empty subdirectory
                os.rmdir(full_dir_path)
                #print(f"Removed empty directory: {full_dir_path}")


def list_paths_at_specific_depth(root_dir, target_depth=4):
    """
    List all unique paths at a specific depth in a directory structure.

    Args:
    root_dir (str): The root directory to start the search.
    target_depth (int, optional): The specific depth of directories to list. Defaults to 4.

    Returns:
    set: A set of unique paths at the specified depth.
    """
    unique_paths = set()

    def _traverse(current_dir, current_depth):
        if current_depth == target_depth:
            unique_paths.add(current_dir)
            return
        elif current_depth > target_depth:
            return

        try:
            for entry in os.listdir(current_dir):
                path = os.path.join(current_dir, entry)
                if os.path.isdir(path):
                    _traverse(path, current_depth + 1)
        except PermissionError:
            pass  # Ignore directories for which you don't have permission

    _traverse(root_dir, 0)
    return unique_paths

def parse_path(this_path, root_end="incoming"):
    """
    Parse a given path and extract components such as root directory, user name, date, etc.

    Args:
    this_path (str): The path to be parsed.
    root_end (str): The predefined value where the root directory ends.

    Returns:
    dict: A dictionary containing the parsed components of the path.
    """
    # Find the index of the root_end in the path
    root_end_index = this_path.find(root_end)
    if root_end_index == -1:
        raise ValueError(f"The root_end '{root_end}' not found in the path.")

    # Include the length of the root_end to get the full root directory
    root_dir = this_path[:root_end_index + len(root_end)]

    # Extract the remaining path components
    remaining_path = this_path[root_end_index + len(root_end):].strip("/")
    keys = remaining_path.split("/")

    facility_user_name = keys[0] if len(keys) > 0 else None
    date = keys[1] if len(keys) > 1 else None
    puck = keys[2] if len(keys) > 2 else None
    dir_type = keys[3] if len(keys) > 3 else None

    result = {
        "root": root_dir,
        "facility_user": facility_user_name,
        "date": date,
        "puck": puck,
        "dir_type": dir_type
    }
    return result


class renaming_object(object):
    """
    A class to handle renaming and moving files and directories based on various attributes.

    Attributes:
    facility_user_name (str): The name of the facility user.
    storage_user_name (str): The name of the storage user.
    origin_paths (list): List of original paths of the files.
    locations (list, optional): List of locations within the path. Defaults to ["screen", "collect"].
    extensions_of_interest (list, optional): List of file extensions of interest. Defaults to ["edf", "img", "cbf"].
    destination_root (str, optional): The root destination path. Defaults to "../data/users".
    facility (str, optional): The name of the facility. Defaults to "ALS".
    derived_result_names (list, optional): List of names for derived results. Defaults to ["XDS", "DIALS", "DIMPLE"].

    Methods:
    execute_move(): Executes the file and directory moving process.
    create_file_destination(source_path, location, sample): Creates a file destination path.
    create_dir_destination(source_path, location, sample, append): Creates a directory destination path.
    create_move_list(): Generates lists of files and directories to be moved.
    make_inventory(): Creates an inventory of files based on certain criteria.
    """

    def __init__(self,
                 facility_user_name,
                 storage_user_name,
                 origin_paths,
                 locations=None,
                 extensions_of_interest=None,
                 destination_root="../data/users",
                 facility="ALS",
                 derived_result_names=None,
                 ):
        if derived_result_names is None:
            derived_result_names = ["XDS", "DIALS", "DIMPLE"]
        if extensions_of_interest is None:
            extensions_of_interest = ["edf", "img", "cbf"]
        if locations is None:
            locations = ["screen", "collect"]
        self.dates = []
        self.facility_user_name = facility_user_name
        self.storage_user_name = storage_user_name
        self.origin_paths = origin_paths
        self.locations = locations
        self.extensions_of_interest = extensions_of_interest
        self.destination_root = destination_root
        self.facility = facility
        self.derived_result_names = derived_result_names

        self.inventory = self.make_inventory()
        self.file_moves, self.dir_moves = self.create_move_list()


        tmp = os.path.join(self.destination_root, self.storage_user_name, "ALS", )
        self.top_levels = []
        for this_date in self.dates:
            self.top_levels.append(os.path.join(tmp, this_date))


    def execute_move(self):
        """
        Execute the process of moving files and directories from the source to the target destinations.
        This method iterates over the lists of files and directories to be moved, creating necessary
        target directories and then moving the files and directories to these locations.
        """

        print("Moving files")
        for source, target_directory in self.file_moves:
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)
            shutil.move(str(source), str(target_directory))

        print("Moving directories with derived data")
        for source, target_directory in self.dir_moves:
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)
            shutil.move(str(source), str(target_directory))

    def create_file_destination(self, source_path, location, sample):
        """
        Create the destination path for a file based on its source path, location, and sample ID.

        Args:
        source_path (str): The source path of the file.
        location (str): The subdirectory location in the source path.
        sample (str): The sample ID related to the file.

        Returns:
        str: The newly created destination path for the file.
        """
        tmp = parse_path(source_path)
        new_path = os.path.join(self.destination_root,
                                self.storage_user_name,
                                self.facility,
                                dates.convert_mdy(tmp['date']),
                                tmp['puck'],
                                sample,
                                location)
        this_date = dates.convert_mdy(tmp['date'])
        if this_date not in self.dates:
            self.dates.append(this_date)
        return new_path

    def create_dir_destination(self, source_path, location, sample, append):
        """
        Create the destination path for a directory based on its source path, location, sample ID, and an additional
        string.

        Args:
        source_path (str): The source path of the directory.
        location (str): The subdirectory location in the source path.
        sample (str): The sample ID related to the directory.
        append (str): An additional string to append to the destination path.

        Returns:
        str: The newly created destination path for the directory.
        """
        tmp = parse_path(source_path)
        new_path = os.path.join(self.destination_root,
                                self.storage_user_name,
                                self.facility,
                                dates.convert_mdy(tmp['date']),
                                tmp['puck'],
                                sample,
                                location,
                                append)
        this_date = dates.convert_mdy(tmp['date'])
        if this_date not in self.dates:
            self.dates.append(this_date)
        return new_path

    def create_move_list(self):
        """
        Generate lists of files and directories to be moved. This method analyzes the inventory
        and prepares a list of source-target pairs for files and directories that need to be moved
        based on the specified criteria.

        Returns:
        tuple: A tuple containing two lists, one for file moves and one for directory moves.
        Each list contains tuples of (source_path, target_directory).
        """
        # now that i have an inventory, i need to make a set of destination paths
        files_moves = []
        dir_moves = []
        for source_path in self.inventory:
            for sample_id in self.inventory[source_path]:
                # I now have to find all stuff associated with this pin
                for location in self.locations:
                    this_path = os.path.join(source_path, location)
                    if os.path.isdir(this_path):
                        file_list = os.listdir(this_path)
                        for f in file_list:
                            if sample_id in f:
                                target = self.create_file_destination(source_path, location, sample_id)
                                s = os.path.join(this_path, f)
                                # what is this
                                is_file = os.path.isfile(s)
                                is_dir = os.path.isdir(s)
                                if is_file:
                                    assert not is_dir
                                if is_file:
                                    # this is a file we need to move over
                                    t = os.path.join(str(target), str(f))
                                    assert sample_id in t
                                    assert sample_id in s
                                    files_moves.append((s, target))
                                if is_dir:
                                    this_method = None
                                    for item in self.derived_result_names:
                                        if item in s:
                                            this_method = item
                                            break
                                    dir_target = self.create_dir_destination(source_path,
                                                                             "processed",
                                                                             sample_id,
                                                                             this_method
                                                                             )
                                    dir_moves.append((s, dir_target))
        return files_moves, dir_moves

    def make_inventory(self):
        """
        Create an inventory of files and directories that need to be processed. This method
        examines each path in the origin paths and compiles a list of samples based on the
        specified file locations and extensions of interest.

        Returns:
        dict: A dictionary with paths as keys and lists of samples as values.
        """
        bucket = {}
        for this_path in self.origin_paths:
            sample_inventory = []
            for this_location in self.locations:
                that_path = os.path.join(this_path, this_location)
                if os.path.isdir(that_path):
                    these_files = os.listdir(that_path)
                    tmp1, tmp2 = ranges.parse_file_list(these_files)
                    for item in tmp1:
                        this_extension = item[0].split(".")[-1]
                        if this_extension in self.extensions_of_interest:
                            this_sample = item[0].split("_")[0]
                            if this_sample not in sample_inventory:
                                sample_inventory.append(this_sample)
            bucket[this_path] = sample_inventory
        return bucket


def process_ALS_data(top_directory, database, incoming="incoming", data="data/users"):
    """
    Main function to orchestrate the file and directory management process.

    Args:
    directory (str): The directory to process.
    database (str): The database file path used for user-related data.
    """
    directory = os.path.join(top_directory, incoming)
    data_directory = os.path.join(top_directory, data)

    n_files = count_files_in_subdirectories(directory)
    print("We start with %i file" % n_files)

    paths = list_paths_at_specific_depth(directory, 3)
    user_db = parse_udb.get_user_bd(database)
    # first we gather all paths
    bucket = {}
    for p in paths:
        tmp = parse_path(p)
        if tmp["facility_user"] not in bucket:
            bucket[tmp["facility_user"]] = []
        this_path = os.path.join(tmp["root"], tmp["facility_user"], tmp["date"], tmp["puck"])
        if this_path not in bucket[tmp["facility_user"]]:
            bucket[tmp["facility_user"]].append(this_path)

    for name in bucket:
        storage_user_name = parse_udb.inverse_search(user_db, name)
        obj = renaming_object(name, storage_user_name, bucket[name],destination_root=data_directory)
        obj.execute_move()
        print(obj.top_levels, "<<----")

        for level in obj.top_levels:
            permissions.set_permissions(level, storage_user_name)
            tmp = permissions.check_permissions(level)

    n_files = count_files_in_subdirectories(directory)
    print("We have %i files left" % n_files)
    assert n_files == 0
    if n_files < 1:
        print("No files left, will remove all empty directories")
        remove_empty_subdirectories(directory)
        return True
    else:
        # Raise an exception if the number of files is not zero
        raise RuntimeError(f"Expected 0 files, but found {n_files} files.")






if __name__ == "__main__":
    process_ALS_data("sbdatacore_test", "incoming/data.base")
