import os
import subprocess
import argparse
import getpass
import tempfile

def create_temp_vault_password_file(password):
    """
    Create a temporary file with the vault password.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
    temp_file.write(password)
    temp_file.close()
    return temp_file.name


def should_process_file(filename, exclude_lower, filetypes_lower):
    """
    Determine whether a file should be processed based on exclusion list and file types.

    :param filename: The name of the file to check.
    :param exclude_lower: A list of filenames to exclude, in lowercase.
    :param filetypes_lower: A list of file extensions to include, in lowercase.
    :return: True if the file should be processed, False otherwise.
    """
    # Check if the filename (in lowercase) is in the exclusion list
    if filename.lower() in exclude_lower:
        return False;

    if filetypes_lower:
        # Check if filetypes is defined and if the filename (in lowercase) ends with any of the defined file types
        return filetypes_lower and any(filename.lower().endswith(ftype) for ftype in filetypes_lower)

    return True

def list_files(directory, exclude, recursive, filetypes):
    """
    List all files in a directory with specific file types, excluding specified files (case-insensitive), .git folders and files, 
    and recursively if specified.
    """
    exclude_lower = [x.lower() for x in exclude]
    filetypes_lower = [ftype.lower() for ftype in filetypes]
    files = []
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [dir for dir in dirs if not dir == '.git'] 
        
        for filename in filenames:
            if not should_process_file(filename, exclude_lower, filetypes_lower):
                continue

            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                files.append(filepath.replace(directory + '/', '', 1))

        if not recursive:
            break
    return files

def run_subprocess(command, cwd, password_file):
    """
    Run a subprocess command, using a temporary password file.
    """
    command += ["--vault-password-file", password_file]
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)

    if result.returncode != 0:
        # Check if the error is because the file is not vault encrypted
        if "input is not vault encrypted data" in result.stderr or "is not a vault encrypted file" in result.stderr:
            print(f"Skipping: '{command[2]}' is not a vault encrypted file.")
            return True  # Return True to skip this file and continue processing others
        else:
            print(f"Error executing {' '.join(command)}: {result.stderr}")
            return False
    return True


def process_files(directory, password, action, preview, verbose, recursive, filetypes):
    """
    Process files for encryption/decryption based on action.
    """
    for file in list_files(directory, [".gitignore"], recursive, filetypes):
        if verbose or preview:
            print(f"{action.title()}ing: {file}")
            
        if not preview:
            password_file = create_temp_vault_password_file(password)
            try:
                action_cmd = ["ansible-vault", action, file]
                if not run_subprocess(action_cmd, directory, password_file):
                    print(f"Failed to {action} file: {file}")
                    exit(1)
            finally:
                os.remove(password_file)

def get_password(prompt="Enter Ansible Vault password: "):
    """
    Prompt the user to enter a password twice and verify they match.
    """
    while True:
        password = getpass.getpass(prompt)
        password_verify = getpass.getpass("Confirm password: ")
        if password == password_verify:
            return password
        else:
            print("Passwords do not match. Please try again.")

def setup_arg_parser():
    """
    Setup argument parser with detailed descriptions for each option.
    """
    parser = argparse.ArgumentParser(
        description="Manage file encryption with Ansible Vault.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "mode",
        choices=["encrypt", "decrypt", "temporary"],
        help=(
            "Mode of operation:\n"
            "\n"
            "encrypt: Encrypt all non-hidden files (except Readme.md) in the directory.\n"
            "decrypt: Decrypt all files in the directory.\n"
            "temporary: Temporarily decrypt files for session use and re-encrypt after pressing Enter.\n"
        )
    )
    parser.add_argument(
        "-p","--preview", 
        action="store_true",
        help="Preview the actions to be taken without making any changes. "
             "Useful for checking what the script will do."
    )
    parser.add_argument(
        "-v","--verbose", 
        action="store_true",
        help="Provide verbose output of the script's actions. "
             "Gives detailed information about the process."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively process files in subdirectories."
    )
    parser.add_argument(
        "-i", "--include-filetypes",
        nargs="*",
        help="Apply actions only to files with the specified extensions (e.g., .yml, .md). Separate multiple types with spaces."
    )
    return parser

def main():
    parser = setup_arg_parser()
    args = parser.parse_args()
    directory = os.getcwd()

    if args.mode in ["encrypt"]:
        password = get_password()
    elif args.mode in ["decrypt", "temporary"]:
        password = getpass.getpass("Enter Ansible Vault password: ")

    filetypes = args.include_filetypes if args.include_filetypes else []

    if args.mode in ["encrypt","decrypt"]:
        process_files(directory, password, args.mode, args.preview, args.verbose, args.recursive, filetypes)
    elif args.mode == "temporary":
        process_files(directory, password, "decrypt", args.preview, args.verbose, args.recursive, filetypes)
        input("Press Enter to re-encrypt files...")
        process_files(directory, password, "encrypt", args.preview, args.verbose, args.recursive, filetypes)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
