#!/usr/bin/env python3
from datetime import datetime as dt
import os
from pathlib import Path
import re
import sys


SCRIPT_DIR = Path(__file__).parent.resolve()
ONE_LINER_FILENAME = SCRIPT_DIR / "license_one_liner.txt"
CONFIG_ENV_FILENAME = SCRIPT_DIR / "config.env"

# File extensions and comment styles
COMMENT_STYLES = {
    # Python
    ".py": "#",
    # JavaScript / TypeScript
    ".js": "//",
    ".ts": "//",
    # Java
    ".java": "//",
    # C / C++
    ".c": "/*",
    ".cpp": "/*",
    ".h": "/*",
    ".hpp": "/*",
    ".hh": "/*",
    # Objective-C
    ".m": "/*",
    ".mm": "/*",
    # Swift
    ".swift": "//",
    # Go
    ".go": "//",
    # Rust
    ".rs": "//",
}

README_LICENSE_TEXT_TEMPLATE = """
{comment} License

This project is free for personal, educational, or non-commercial use under the MIT License (see LICENSE-MIT.txt).

Commercial use requires a separate license (see LICENSE-COMMERCIAL.txt).
"""


def unquote(value: str) -> str:
    # Support empty values. Also support just setting to " or '
    if len(value) < 2:
        return value
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_file(filename: str | Path, encoding: str | None = "UTF-8") -> str | bytes:
    open_flags = "r" if encoding else "rb"
    kwargs = {"encoding": encoding} if encoding else {}
    with open(filename, open_flags, **kwargs) as handle:
        return handle.read()


def read_env(filename: str | Path) -> dict:
    data = {}
    with open(filename, "r", encoding="UTF-8") as handle:
        for idx, line in enumerate(handle.readlines()):
            line = line.strip()
            # Minor comment support
            if line.startswith("#"):
                continue
            parts = line.split("=")
            if len(parts) != 2:
                raise ValueError(f"Env file bad format on line {idx} (values and keys can't have '='): '{filename}'")
            key = parts[0]
            if not key:
                raise ValueError(f"Line {idx} had an empty key (not allowed)")
            value = unquote(parts[1])
            data[key] = value
    return data


def load_one_liner() -> str:
    return load_file(ONE_LINER_FILENAME).strip()


def load_config_env() -> dict:
    config_env = read_env(CONFIG_ENV_FILENAME)
    required_keys = [
        "[CONTACT_EMAIL]",
        "[CONTACT_HANDLE]",
    ]
    for key in required_keys:
        if key not in config_env:
            raise KeyError(f"Required key '{key}' was not found in config file '{CONFIG_ENV_FILENAME}'")

    # Supports a default
    if not config_env["[YEAR]"]:
        # NOTE: This uses en-dash because that's proper for date ranges.
        # Using "–present" indicates clear "this is still under development", but is not required for legal protection
        config_env["[YEAR]"] = f"{dt.now().year())}–present"

    if not config_env["[COPYRIGHT_HOLDER]"]:
        # Default value for this based on other values that are required
        config_env["[COPYRIGHT_HOLDER]"] = config_env["[CONTACT_HANDLE]"]
        if config_env["[CONTACT_NAME]"]:
            config_env["[COPYRIGHT_HOLDER]"] += " (" + config_env["[CONTACT_NAME]"] + ")"

    if not config_env["[CONTACT_INFO]"]:
        # Default value for this based on other values that are required
        config_env["[CONTACT_INFO]"] = config_env["[COPYRIGHT_HOLDER]"] + ": " + config_env["[CONTACT_EMAIL]"]

    return config_env


def load_license_filenames() -> list[Path]:
    filenames = []
    for filename in os.listdir(SCRIPT_DIR):
        if filename.startswith("LICENSE"):
            filenames.append(SCRIPT_DIR / filename)
    return filenames


def load_license_templates() -> dict[Path, str]:
    return {filename: load_file(filename) for filename in load_license_filenames()}


def insert_python_header(content, spdx_line):
    """Insert SPDX header respecting shebang and module docstring"""
    lines = content.splitlines(keepends=True)
    idx = 0

    # Skip shebang
    if lines and lines[0].startswith("#!"):
        idx = 1

    # Check for module docstring
    docstring_match = re.match(r'\s*(["\']{3}|["\'])', lines[idx] if idx < len(lines) else "")
    if docstring_match:
        quote = docstring_match.group(1)
        for j in range(idx + 1, len(lines)):
            if lines[j].strip().endswith(quote):
                lines.insert(idx + 1, spdx_line + "\n")
                return "".join(lines)
        # fallback
        lines.insert(idx + 1, spdx_line + "\n")
        return "".join(lines)
    else:
        lines.insert(idx, spdx_line + "\n")
        return "".join(lines)


def insert_block_comment_header(lines, spdx_line, comment_style):
    """
    Insert SPDX header inside existing top comment block if present, otherwise prepend.
    Supports /* */ and // comments.
    """
    if not lines:
        return spdx_line + "\n\n"

    first_line = lines[0].lstrip()
    # Multi-line block comment
    if comment_style == "/*":
        if first_line.startswith("/*"):
            # Find closing */
            for i, line in enumerate(lines):
                if "*/" in line:
                    lines.insert(i, " " + spdx_line + "\n")
                    return "".join(lines)
        # No block, prepend with proper ending
        return spdx_line + " */\n\n" + "".join(lines)
    # Single-line comment style
    else:
        if first_line.startswith(comment_style):
            # Insert after first comment line
            lines.insert(1, spdx_line + "\n")
            return "".join(lines)
        return spdx_line + "\n\n" + "".join(lines)


def add_header_to_file(file_path, comment_style, spdx_line):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "SPDX-License-Identifier: MIT-NC" in content:
        return False

    if file_path.endswith(".py"):
        new_content = insert_python_header(content, spdx_line)
    else:
        ines = content.splitlines(keepends=True)
        new_content = insert_block_comment_header(lines, spdx_line, comment_style)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def format_content(content: str, config_dict: dict) -> str:
    for key, value in config_dict.items():
        if key in content:
            content = content.replace(key, value)
    return content


def update_readme(readme_filename: str | Path) -> None:
    comment_chars = {
        ".adoc": ["=", "==", "==="],
        ".md": ["#"],
        ".txt": ["#"],
        # For files just named "README"
        "": ["#"],
    ]
    ext = os.splitext(readme_filename)[1].lower()
    comment_chars = comment_char.get(ext, ["#"])
    with open(readme_filename, "r", encoding="UTF-8") as handle:
        for line in handle.readlines():
            for comment_char in comment_chars:
                if line.lower().startswith(f"{comment_char} license"):
                    print(f"README file '{readme_filename}' already had a licensing section")
                    return

    # Put a licensing section at the end of the file
    with open(readme_filename, "a", encoding="UTF-8") as handle:
        # Formatting
        handle.write("\n")
        handle.write(README_LICENSE_TEXT_TEMPLATE.format(comment=comment_chars[0]))
        print(f"README file '{readme_filename}' updated with a licensing section")


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-add license info to a repository")
    parser.add_argument("root", help="Root directory of repo")
    parser.add_argument("-p", "--project-name", help="Project name of repo (use the casing you want it known by)")
    parser.add_argument("-v", "--verbose", help="Print extra outputs", action="store_true")
    parser.add_argument("--no-git", help="Don't check for given directory being a git repo", action="store_true")
    parsed = parser.parse_args()

    one_liner_content = load_one_liner()
    config_env = load_config_env()
    if not parsed.project_name:
        if not config["[PROJECT_NAME]"]:
            print(f"[!] Project name must be given in config.env file or on command-line", file=sys.stderr)
            return 1
    else:
        # Command-line value takes precedence
        config["[PROJECT_NAME]"] = parsed.project_name

    if not parsed.no_git:
        expected_git_dir = os.path.join(parsed.root, ".git")
        if not os.path.isdir(expected_git_dir):
            print(f"[!] Root path is expected to be a directory and also contain a .git sub-directory", file=sys.stderr)
            return 1

    license_file_templates = load_license_templates()
    license_files = {filename: format_content(content) for filename, content in license_file_templates.items()}
    for filename, content in license_file_templates.items():
        out_filename = parsed.root / filename
        with open(out_filename, "w") as handle:
            handle.write(format_content(content, config_env))
        print(f"[+] Just created license file '{out_filename}'")

    spdx_lines_added = 0
    for root, dirs, files in os.walk(parsed.root):
        for file in files:
            if file.lower().startswith("readme")
                file_path = os.path.join(root, file)
                update_readme(file_path)
                continue

            ext = os.path.splitext(file)[1].lower()
            if ext in COMMENT_STYLES:
                file_path = os.path.join(root, file)
                comment_style = COMMENT_STYLES[ext]
                spdx_line = f"{comment_style} {format_content(one_liner_content)}"
                if add_header_to_file(file_path, comment_style, spdx_line):
                    spdx_lines_added += 1
                    print(f"[+] Added SPDX header to: {file_path}")
            elif parsed.verbose:
                print(f"[_] File didn't match a known file extension: '{filename}'")

    print(f"\n[+] Done! SPDX headers added to {spdx_lines_added} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
