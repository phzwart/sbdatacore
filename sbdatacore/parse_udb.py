def get_user_bd(user_database):
    """
    Reads a user database file and creates a dictionary mapping users to data names.

    The function reads a file, where each line is expected to have a format of 'username data_name'.
    Lines beginning with '#' are treated as comments and ignored.

    Args:
    user_database (str): The path to the user database file.

    Returns:
    dict: A dictionary where keys are usernames and values are lists of associated data names.
    """
    result = {}
    with open(user_database, 'r') as f:
        for line in f:
            if "#" not in line:
                items = line.strip().split(" ")
                if len(items) >= 2:
                    nersc_name, data_name = items[0], items[1]
                    result.setdefault(nersc_name, []).append(data_name)

    return result


def inverse_search(user_bd, item):
    """
    Performs an inverse search in the user database dictionary to find the key for a given item.
    Raises an error if the item is found in more than one key's list.

    Args:
    user_bd (dict): The user database dictionary.
    item (str): The item to search for in the values of the dictionary.

    Returns:
    str: The key corresponding to the found item.

    Raises:
    ValueError: If the item is not found or found in multiple keys.
    """
    found_key = None

    for key, values in user_bd.items():
        if item in values:
            if found_key is not None:  # Item found in another key's list already
                raise ValueError(f"Item '{item}' is not uniquely associated with a single key.")
            found_key = key

    if found_key is None:
        raise ValueError(f"Item '{item}' not found in any key.")

    return found_key






