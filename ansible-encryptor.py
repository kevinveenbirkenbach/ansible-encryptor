import os
import subprocess
import argparse
import getpass

def list_files(directory, exclude):
    """
    List all files in a directory, excluding specified files and hidden files.
    """
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.') and f not in exclude]

def run_subprocess(command, cwd):
    """
    Run a subprocess command and handle errors.
    """
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing {' '.join(command)}: {result.stderr}")
        return False
    return True

def process_files(directory, password, action, preview=False, verbose=False):
    """
    Process files for encryption/decryption based on action.
    """
    for file in list_files(directory, ["Readme.md"]):
        if action == "encrypt" and not file.endswith(".vault"):
            target_file = file + ".vault"
            action_cmd = ["ansible-vault", "encrypt", file, "--vault-password", password]
        elif action == "decrypt" and file.endswith(".vault"):
            target_file = file.replace(".vault", "")
            action_cmd = ["ansible-vault", "decrypt", file, "--vault-password", password]
        else:
            continue

        if verbose or preview:
            print(f"{action.title()}ing: {file} -> {target_file}")

        if not preview:
            subprocess.run(action_cmd, cwd=directory)
            os.rename(os.path.join(directory, file), os.path.join(directory, target_file))
            
        if not preview:
            if not run_subprocess(action_cmd, directory):
                print(f"Failed to {action} file: {file}")
                exit(1)
            os.rename(os.path.join(directory, file), os.path.join(directory, target_file))

def update_gitignore(directory, mode):
    """
    Update .gitignore to include/exclude files based on mode.
    """
    gitignore_path = os.path.join(directory, ".gitignore")
    if mode == "encrypt":
        with open(gitignore_path, "w") as gitignore:
            gitignore.write("*\n!*.vault\n!Readme.md\n")
    elif mode == "decrypt":
        if os.path.exists(gitignore_path):
            os.remove(gitignore_path)

def main():
    parser = argparse.ArgumentParser(description="Manage file encryption with Ansible Vault.")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt files.")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt files.")
    parser.add_argument("--open", action="store_true", help="Decrypt files temporarily.")
    parser.add_argument("--close", action="store_true", help="Remove decrypted files.")
    parser.add_argument("--temporary", action="store_true", help="Temporarily open files.")
    parser.add_argument("--preview", action="store_true", help="Preview actions without making changes.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")

    args = parser.parse_args()
    directory = os.getcwd()

    if args.encrypt or args.decrypt or args.temporary:
        password = getpass.getpass("Enter Ansible Vault password: ")

    if args.encrypt:
        process_files(directory, password, "encrypt", args.preview, args.verbose)
    elif args.decrypt or args.open:
        process_files(directory, password, "decrypt", args.preview, args.verbose)
    elif args.temporary:
        process_files(directory, password, "decrypt", args.preview, args.verbose)
        input("Press Enter to re-encrypt files...")
        process_files(directory, password, "encrypt", args.preview, args.verbose)
    elif args.close:
        for file in list_files(directory, ["Readme.md"]):
            if not file.endswith(".vault"):
                os.remove(os.path.join(directory, file))
    
    if args.encrypt or args.decrypt:
        update_gitignore(directory, "encrypt" if args.encrypt else "decrypt")

if __name__ == "__main__":
    main()
