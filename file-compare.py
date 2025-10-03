#!/bin/python3

"""
File Comparison Utility

This script provides a comprehensive tool for comparing two files using various methods:
- Hash comparison (MD5 and SHA1)
- Size comparison
- Byte-level comparison
- Symlink detection

Usage:
    python3 file-compare.py --file1 /path/to/file1 --file2 /path/to/file2 [options]

Options:
    --hash       Display file hash information
    --size       Compare file sizes
    --compare    Perform file content comparison
    --symlink    Check symlink status

Dependencies:
    - Python 3.7+
    - Standard library modules: os, mmap, shutil, filecmp, hashlib, argparse
"""

import os
import sys
import mmap
import shutil
import filecmp
import hashlib
import argparse
import platform

def parse_args() -> argparse:
    """
    Parse command-line arguments for file comparison utility.

    This function sets up an argument parser to handle command-line inputs for comparing two files
    with various optional comparison methods.

    Returns:
        argparse.Namespace: An object containing parsed command-line arguments with the following attributes:
            - file1 (str): Required path to the first file to be compared
            - file2 (str): Required path to the second file to be compared
            - hash (bool): Flag to output hash information (optional)
            - size (bool): Flag to output file size comparison (optional)
            - compare (bool): Flag to output file comparison results (optional)
            - symlink (bool): Flag to output symlink information (optional)

    Example:
        $ python3 file-compare.py --file1 /path/to/file1 --file2 /path/to/file2 --hash --size

    Raises:
        SystemExit: If required arguments are missing or invalid arguments are provided
    """

    parser = argparse.ArgumentParser(
        description="Compare two files using several methods",
        epilog="Example: python3 file-compare.py --file1 /path/to/file1 --file2 /path/to/file2 [--hash] [--size] [--compare] [--symlink]",
    )

    # Add arguments for two files
    parser.add_argument("--file1", required=True, help="Path to the first file")
    parser.add_argument("--file2", required=True, help="Path to the second file")

    # Optional flags for specific outputs
    parser.add_argument("--hash", action="store_true", help="Output hash information")
    parser.add_argument(
        "--size", action="store_true", help="Output file size comparison"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Output file comparison results"
    )
    parser.add_argument(
        "--symlink", action="store_true", help="Output symlink information"
    )

    args = parser.parse_args()
    return args

def is_fips_enabled() -> bool:
    if sys.platform.startswith('linux'):
        try:
            with open('/proc/sys/crypto/fips_enabled', 'r') as f:
                return f.read().strip() == '1'
        except FileNotFoundError:
            return False
    elif sys.platform == 'darwin':  # macOS check
        try:
            import subprocess
            result = subprocess.run(['grep', '-l', 'fips_ssh_config', '/private/etc/ssh/ssh_config.d/*'],
                                    capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except Exception:
            return False
    elif sys.platform == 'win32':  # Windows-specific FIPS check
        try:
            # Windows FIPS mode check
            import winreg

            # Check FIPS configuration in Windows registry
            try:
                # Open the registry key for FIPS configuration
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Lsa\FipsAlgorithmPolicy"
                )
                # Read the Enabled value
                fips_enabled, _ = winreg.QueryValueEx(key, "Enabled")
                return bool(fips_enabled)
            except FileNotFoundError:
                return False
            except PermissionError:
                # Handle cases where registry access is restricted
                return False
        except ImportError:
            # winreg module not available (unlikely on Windows)
            return False
    return False


def file_size_compare(file1, file2) -> tuple:
    """
    Compare the sizes of two files.

    This function performs a size comparison between two files, checking their existence,
    ensuring they are not directories, and calculating size differences.

    Args:
        file1 (str): Path to the first file to be compared
        file2 (str): Path to the second file to be compared

    Returns:
        tuple or dict: A tuple containing:
            - size1 (int): Size of the first file in bytes
            - size2 (int): Size of the second file in bytes
            - size_difference (int): Absolute difference between file sizes
            - is_same_size (bool): True if files are the same size, False otherwise

        Returns a dictionary with an error message in these cases:
            - If one or both files do not exist
            - If either path is a directory

        Returns None if a PermissionError occurs (e.g., insufficient file access permissions)

    Raises:
        No explicit exceptions raised; errors are handled within the function

    Example:
        >>> file_size_compare('/path/to/file1.txt', '/path/to/file2.txt')
        (1024, 2048, 1024, False)
    """

    try:
        if not os.path.exists(file1) and not os.path.exists(file2):
            return {"error": "One of both of the files do not exist"}
        if os.path.isdir(file1) or os.path.isdir(file2):
            return {"error": "Cannot compare directory sizes"}

        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)

        return (size1, size2, (abs(size1 - size2)), (size1 == size2))
    except PermissionError:
        return


def get_hashes(filepath) -> dict:
    """
    Calculate both MD5 and SHA1 hashes for a file.

    If the system is in FIPS mode, only returns SHA1 hash.

    Args:
        filepath (str): Path to the file to be hashed

    Returns:
        dict: A dictionary containing hash values
    """
    # Check FIPS mode
    fips_mode = is_fips_enabled()

    with open(filepath, "rb") as f:
        # Memory-map the file
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # If FIPS mode is enabled, only return SHA1
            if fips_mode:
                return {
                    "sha1": hashlib.sha1(mm).hexdigest(),
                    "fips_mode": True
                }

            # If FIPS mode is disabled, return both hashes
            return {
                "md5": hashlib.md5(mm).hexdigest(),
                "sha1": hashlib.sha1(mm).hexdigest(),
                "fips_mode": False
            }


def compare_files(file1, file2, shallow=True) -> bool:
    """
    Compare two files with optional shallow or deep comparison.

    Args:
        file1 (str): Path to first file
        file2 (str): Path to second file
        shallow (bool, optional): Whether to use shallow comparison. Defaults to True.

    Returns:
        bool: Whether files are identical
    """
    file_compare = filecmp.cmp(file1, file2, shallow=shallow)

    comparison_type = "shallow" if shallow else "deep"
    print(
        f"Byte comparing {file1} and {file2} ({comparison_type}). Result: {file_compare}"
    )

    return file_compare


def same_file(file1, file2) -> bool:
    """
    Determine if two file paths refer to the same file on the filesystem.

    This function checks whether the two given file paths point to the exact same file,
    taking into account filesystem-level file identification (including hard links).

    Args:
        file1 (str): The path to the first file.
        file2 (str): The path to the second file.

    Returns:
        bool: True if the files are the same, False otherwise.

    Raises:
        FileNotFoundError: If either of the file paths does not exist.
        PermissionError: If there are insufficient permissions to access the files.

    Examples:
        >>> same_file('/home/user/document.txt', '/home/user/document.txt')
        True
        >>> same_file('/home/user/document.txt', '/home/user/copy_of_document.txt')
        False
    """
    file_compare = os.path.samefile(file1, file2)

    return file_compare


def main() -> bool:
    args = parse_args()
    # Determine if all functions should run/print
    print_all = not (args.hash or args.size or args.compare or args.symlink)
    # Set up terminal width for divider
    terminal_width = shutil.get_terminal_size().columns
    divider = "-" * terminal_width

    # Hash output
    if args.hash or print_all:
        print(divider)
        file1_hashes = get_hashes(args.file1)
        file2_hashes = get_hashes(args.file2)

        # Print hash information
        print(f"FIPS Mode: {file1_hashes.get('fips_mode', False)}")

        if not file1_hashes.get('fips_mode', False):
            print(f"{args.file1} MD5 hash: {file1_hashes['md5']}")
            print(f"{args.file2} MD5 hash: {file2_hashes['md5']}")

        print(f"{args.file1} SHA1 hash: {file1_hashes['sha1']}")
        print(f"{args.file2} SHA1 hash: {file2_hashes['sha1']}")

    # Size comparison
    if args.size or print_all:
        print(divider)
        size_compare = file_size_compare(args.file1, args.file2)
        print(f"{args.file1} size (bytes): {size_compare[0]}")
        print(f"{args.file2} size (bytes): {size_compare[1]}")
        print(f"Size difference (bytes): {size_compare[2]}")
        print(f"Are the same size: {size_compare[3]}")

    # File comparison
    if args.compare or print_all:
        print(divider)
        compare_files(args.file1, args.file2, shallow=True)
        compare_files(args.file1, args.file2, shallow=False)

    # Symlink information
    if args.symlink or print_all:
        print(divider)
        print(f"Is {args.file1} a symlink: {os.path.islink(args.file1)}")
        print(f"Is {args.file2} a symlink: {os.path.islink(args.file2)}")
        print(
            f"Are {args.file1} and {args.file2} the same file on disk: "
            f"{same_file(args.file1, args.file2)}"
        )
    return 0

if __name__ == "__main__":
    main()
