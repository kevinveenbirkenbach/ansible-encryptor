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

def list_files(directory, exclude, recursive):
    """
    List all files in a directory, excluding specified files, hidden files, 
    and recursively if specified.
    """
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Filter versteckte Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            if filename.startswith('.'):
                continue  # Versteckte Dateien überspringen
            if filename in exclude:
                continue  # Ausgeschlossene Dateien überspringen

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
        print(f"Error executing {' '.join(command)}: {result.stderr}")
        return False
    return True

def process_files(directory, password, action, preview=False, verbose=False, recursive=False):
    """
    Process files for encryption/decryption based on action.
    """
    for file in list_files(directory, ["Readme.md"], recursive):
        if action == "encrypt" and not file.endswith(".vault"):
            target_file = file + ".vault"
            action_cmd = ["ansible-vault", "encrypt", file]
        elif action == "decrypt" and file.endswith(".vault"):
            target_file = file.replace(".vault", "")
            action_cmd = ["ansible-vault", "decrypt", file]
        else:
            continue

        if verbose or preview:
            print(f"{action.title()}ing: {file} -> {target_file}")
            
        if not preview:
            password_file = create_temp_vault_password_file(password)
            try:
                if not run_subprocess(action_cmd, directory, password_file):
                    print(f"Failed to {action} file: {file}")
                    exit(1)
                os.rename(os.path.join(directory, file), os.path.join(directory, target_file))
            finally:
                os.remove(password_file)

def update_gitignore(directory, mode, preview=False, verbose=False):
    """
    Update .gitignore to include/exclude files based on mode, or preview changes.
    """
    gitignore_path = os.path.join(directory, ".gitignore")
    
    if verbose:
        action = "Creating" if mode == "encrypt" else "Removing"
        print(f"{action} .gitignore entries for mode: {mode}")
        
    if preview:
        return

    if mode == "encrypt":
        with open(gitignore_path, "w") as gitignore:
            gitignore.write("*\n!*.vault\n!Readme.md\n")
    elif mode == "decrypt":
        if os.path.exists(gitignore_path):
            os.remove(gitignore_path)

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

def close_files(directory, preview=False, verbose=False):
    """
    Remove or preview removal of decrypted files.
    """
    files_to_remove = [f for f in list_files(directory, ["Readme.md"]) if not f.endswith(".vault")]
    if not files_to_remove:
        print("No files to remove.")
        return

    if verbose or preview:
        print("The following files will be removed:" if not preview else "Files to be removed:")
        for file in files_to_remove:
            print(file)

    if not preview:
        for file in files_to_remove:
            os.remove(os.path.join(directory, file))
            if verbose:
                print(f"Removed: {file}")

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
        choices=["encrypt", "decrypt", "open", "close", "temporary"],
        help=(
            "Mode of operation:\n"
            "\n"
            "encrypt:\n"
            "Encrypt all non-hidden files (except Readme.md) in the directory.\n"
            "Updates .gitignore to exclude non-vault files.\n"
            "\n"
            "decrypt:\n"
            "Decrypt all .vault files in the directory.\n"
            "Updates .gitignore to include decrypted files.\n"
            "\n"
            "open:\n"
            "Temporarily decrypt .vault files for viewing/editing without modifying .gitignore.\n"
            "\n"
            "close:\n"
            "Re-encrypt decrypted files and remove them from the directory. Used after 'open' or 'temporary'.\n"
            "\n"
            "temporary:\n"
            "Temporarily decrypt files for session use and re-encrypt after pressing Enter.\n"
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
    return parser

def main():
    parser = setup_arg_parser()
    args = parser.parse_args()
    directory = os.getcwd()

    if args.mode in ["encrypt", "close"]:
        password = get_password()
    elif args.mode in ["decrypt", "open", "temporary"]:
        password = getpass.getpass("Enter Ansible Vault password: ")

    if args.mode in "encrypt":
        process_files(directory, password, args.mode, args.preview, args.verbose, args.recursive)
        update_gitignore(directory, args.mode, args.preview, args.verbose)
    elif args.mode == "decrypt":
        process_files(directory, password, args.mode, args.preview, args.verbose, args.recursive)
        update_gitignore(directory, args.mode, args.preview, args.verbose)
    elif args.mode == "open":
        process_files(directory, password, "decrypt", args.preview, args.verbose, args.recursive)
    elif args.mode == "close":
        process_files(directory, password, "encrypt", args.preview, args.verbose, args.recursive)
    elif args.mode == "temporary":
        process_files(directory, password, "decrypt", args.preview, args.verbose, args.recursive)
        input("Press Enter to re-encrypt files...")
        process_files(directory, password, "encrypt", args.preview, args.verbose, args.recursive)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
