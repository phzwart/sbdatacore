import os
import parse_udb
import ranges

def list_paths_at_specific_depth(root_dir, target_depth=4):
    """
    Lists all unique paths at a specific depth in a directory.

    Args:
    root_dir (str): The root directory to start the search.
    target_depth (int): The specific depth of directories to list.

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

def parse_path(this_path):
    keys = this_path.split("/")
    root_dir = keys[0]
    facility_user_name = keys[1]
    date = keys[2]
    puck = keys[3]
    dir_type = None
    if len(keys) > 4:
        dir_type = keys[4]

    result = {
        "root": root_dir,
        "facility_user": facility_user_name,
        "date": date,
        "puck":puck,
        "dir_type": dir_type
    }
    return result


class renaming_object(object):
    def __init__(self,
                 facility_user_name,
                 storage_user_name,
                 origin_paths,
                 locations = ["screen", "collect"],
                 extensions_of_interest = ["edf", "img", "cbf"]
                 ):
        self.facility_user_name = facility_user_name
        self.storage_user_name = storage_user_name
        self.origin_paths = origin_paths
        self.locations = locations
        self.extensions_of_interest = extensions_of_interest

        self.inventory = self.make_inventory()

    def create_destination(self):
        None

    def make_inventory(self):
        """
        check each path and find all pins
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









def process_ALS_data(directory, database):
    paths = list_paths_at_specific_depth(directory,3)
    user_db = parse_udb.get_user_bd(database)
    #first we gather all paths
    bucket = {}
    for p in paths:
        tmp = parse_path(p)
        if tmp["facility_user"] not in bucket:
            bucket[tmp["facility_user"]] = []
        this_path = os.path.join( tmp["root"],tmp["facility_user"],tmp["date"],tmp["puck"] )
        if this_path not in bucket[tmp["facility_user"]]:
            bucket[tmp["facility_user"]].append(this_path)


    for name in bucket:
        print(name)
        obj = renaming_object(name, "tmpppp", bucket[name])










if __name__ =="__main__":
    process_ALS_data("./", "data.base")
