# Ansible Encrypter CLI (ansenc) 🔐

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html) [![GitHub stars](https://img.shields.io/github/stars/kevinveenbirkenbach/ansible-encrypter.svg?style=social)](https://github.com/kevinveenbirkenbach/ansible-encrypter/stargazers)

Ansible Encrypter CLI (ansenc) is a powerful command-line tool for managing file encryption and decryption using Ansible Vault. It helps you securely encrypt files within your current directory (and its subdirectories if desired) with ease, and supports temporary decryption sessions for on-the-fly editing.

---

## 🛠 Features

- **Encryption & Decryption:** Encrypt and decrypt files using Ansible Vault.
- **Temporary Mode:** Decrypt files temporarily, then re-encrypt them after your session.
- **Selective Processing:** Apply actions only to specific file types.
- **Recursive Traversal:** Process files recursively through subdirectories.
- **Preview Mode:** Preview changes before actually applying them.
- **Verbose Output:** Get detailed logs of every operation for full transparency.

---

## 📥 Installation

Install Ansible Encrypter CLI using [Kevin's Package Manager](https://github.com/kevinveenbirkenbach/package-manager) under the alias `ansenc`:

```bash
package-manager install ansenc
```

This command installs ansenc globally, making it available in your terminal. 🚀

---

## 🚀 Usage

Run Ansible Encrypter CLI from the command line to encrypt, decrypt, or temporarily decrypt files in your current directory.

### Basic Examples

- **Encrypt Files:**
  ```bash
  ansenc encrypt
  ```
  Prompts you to enter and confirm your Ansible Vault password, then encrypts all applicable files in the current directory.

- **Decrypt Files:**
  ```bash
  ansenc decrypt
  ```
  Prompts for your vault password and decrypts all files matching the specified criteria.

- **Temporary Decryption:**
  ```bash
  ansenc temporary
  ```
  Decrypts files temporarily; after you press Enter, the files are re-encrypted.

### Options

- **`--preview`**: Show what changes would be made without modifying any files.
- **`--verbose`**: Display detailed log information during processing.
- **`--recursive`**: Process files in all subdirectories.
- **`--include-filetypes`**: Specify file extensions (e.g., `.yml`, `.md`) to limit processing.

Example with options:
```bash
ansenc encrypt --recursive --include-filetypes .yml .md --verbose
```

Run `ansenc --help` for a complete list of options and usage details.

---

## 🧑‍💻 Author

Developed by **Kevin Veen-Birkenbach**  
- 📧 [kevin@veen.world](mailto:kevin@veen.world)  
- 🌐 [https://www.veen.world/](https://www.veen.world/)

---

## 📜 License

This project is licensed under the **GNU Affero General Public License, Version 3, 19 November 2007**.  
See the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributions

Contributions are welcome! Feel free to fork the repository, submit pull requests, or open issues to help improve Ansible Encrypter CLI. Let’s keep your files secure and your workflow efficient! 😊
