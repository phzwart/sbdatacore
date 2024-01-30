import os
import subprocess

def set_permissions(directory, user):
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            subprocess.run(["setfacl", "-b", full_path])
            # Set permissions so that only the owner can access
            os.chmod(full_path, 0o700)

            # Add ACL entry for the specified user
            subprocess.run(["setfacl", "-m", f"u:{user}:rwx", full_path])

def check_permissions(directory):
    report = []
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            full_path = os.path.join(root, name)

            # Get permissions
            permissions = oct(os.stat(full_path).st_mode)[-3:]
            report.append(f"Permissions for {full_path}: {permissions}")

            # Get ACLs
            acl_info = subprocess.check_output(["getfacl", "-p", full_path])
            report.append(f"ACLs for {full_path}:\n{acl_info.decode()}")

    return report
