import os
from sbdatacore import ranges


def touch(file_path):
    """
    Mimics the Unix touch command by creating an empty file if it does not exist,
    or updating the modification time if it does.

    Args:
    file_path (str): Path to the file to be touched.
    """
    with open(file_path, 'a'):
        os.utime(file_path, None)


def build_ALS_data(base_dir, user, date, puck, pin, collect, screen_sets, collect_sets):
    screen_path = os.path.join(base_dir, user, date, puck, "screen")
    screen_files = []
    screen_exts = ["cbf", "txt", "jpg"]

    for ii in range(screen_sets):
        for jj in range(1, 3):
            for ext in screen_exts:
                fname = pin + "_%i_0000%i." % (ii, jj) + ext
                screen_files.append(fname)

    data_path = None
    data_files = []
    xds_path = None
    dials_path = None

    if collect:
        data_path = os.path.join(base_dir, user, date, puck, "collect")
        data_files = []
        for ii in range(1, collect_sets + 1):
            base_name = pin + "_%i_#####.cbf" % ii
            obj = ranges.SerialFileNameHandler(base_name)
            for f in obj.names_from_range("1-12"):
                data_files.append(f)
            xds_path = os.path.join(data_path, "XDS_" + pin + "_%i" % ii)
            dials_path = os.path.join(data_path, "DIALS_" + pin + "_%i" % ii)

    package = {
        "screen_path": screen_path,
        "screen_files": screen_files,
        "collect_path": data_path,
        "collect_files": data_files,
        "xds_path": xds_path,
        "dials_path": dials_path
    }
    return package

def simulate_ALS_runs(base_dir):
    base_dir = os.path.join(base_dir, "incoming")
    users = ["kamala", "kamala", "mike", "mike", "mike"]
    dates = ["12323", "121223", "010124", "021224", "021224"]
    pucks = ["snoopy", "peanut", "mother", "mother", "mother"]
    pins = ["Pin1", "Pin2", "Pin1", "Pin2", "Pin3"]
    collect = [True, True, False, True, True]
    for u, d, pu, pi, c in zip(users, dates, pucks, pins, collect):
        tmp = build_ALS_data(base_dir, u, d, pu, pi, c, 1, 1)
        screen_path = tmp['screen_path']
        if screen_path is not None:
            os.makedirs(screen_path, exist_ok=True)
            for f in tmp['screen_files']:
                this_tmp = os.path.join(screen_path, f)
                touch(this_tmp)

        collect_path = tmp['collect_path'] if tmp['collect_path'] else None  # Update the path
        if collect_path is not None:
            os.makedirs(collect_path, exist_ok=True)
            os.makedirs(os.path.join(tmp['xds_path']), exist_ok=True)
            os.makedirs(os.path.join(tmp['dials_path']), exist_ok=True)
            touch(os.path.join(tmp['xds_path'], "results.txt"))
            touch(os.path.join(tmp['dials_path'], "results.txt"))

            for f in tmp['collect_files']:
                this_tmp = os.path.join(collect_path, f)
                touch(this_tmp)

def build_fake_database(filename):
    f = open(filename, 'w')
    userdatabase="""#NERSC FACILITY
kharris kamala
mpence mike
mpence mikey"""
    print(userdatabase,file=f)


def run():
    os.makedirs("sbdatacore_test/incoming", exist_ok=True)  # Create incoming directory
    os.makedirs("sbdatacore_test/data", exist_ok=True)      # Create data directory
    build_fake_database("sbdatacore_test/data.base")        # Update the database file path
    simulate_ALS_runs("sbdatacore_test/")



if __name__ == "__main__":
    run()
