import os
import sys
from sbdatacore import parse_ALS_data
from sbdatacore import make_summary
from sbdatacore import parse_udb

def print_usage():
    help_txt = """\n\n\n
sbdatacore.handout_ALS_data <path to top level sbdatacore directory>\n\n\n

The data is supposed to be stored like this

FACILITY_UID/<date>/<puckname>/screen/Pin1_0_0001.img
etc etc

and

FACILITY_UID/<date>/<puckname>/collect/Pin1_1_0001.img
etc etc

"""
    print(help_txt)

    print_UDB_help()

def print_UDB_help():
    help_txt = """

A userdatabse must be defined as environmental variable SBDATACORE_UDB

export SBDATACORE_UDB=path/to/the/file

A user database is a simple text file that looks like this

NERSC_UID FACILITY_UID

The NERSC_UID is the user ID at the storage system (NERSC)
The FACILITY_UID is the name of the top level director
"""
    print(help_txt)


def main():
    if len(sys.argv) != 2:
        print_usage()
        raise RuntimeError("Expected instructions on top-level directory")

    # find the user data base

    # Get the environment variable
    user_db = os.environ.get('SBDATACORE_UDB')

    # Check if the variable was found and print it
    if user_db is not None:
        print(f"SBDATACORE_UDB: {user_db}")
        print()
        print("These users are defined:")
        print(parse_udb.get_user_bd(user_db))
        print()

    else:
        print("SBDATACORE_UDB is not set.")
        raise RuntimeError("Please define a user database file")

    tmp = make_summary.list_dirs_with_file_count( os.path.join(sys.argv[1], "incoming") )
    print("Content of incoming")
    print(tmp)
    parse_ALS_data.process_ALS_data(sys.argv[1], user_db)
    tmp = make_summary.list_dirs_with_file_count( os.path.join(sys.argv[1], "data/users") )
    print()
    print("Content of data/users")
    print(tmp)







