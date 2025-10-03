# File Comparison Utility

## Overview

A powerful Python utility for comparing files using multiple methods, including hash calculation, size comparison, content comparison, and symlink detection.

## Features

- 🔍 **Multiple Comparison Methods**:
  - Hash comparison (MD5 and SHA1)
  - File size comparison
  - Byte-level file content comparison
  - Symlink detection

- 💻 **Flexible Command-Line Interface**
- 📊 **Detailed Output Options**

## Prerequisites

### System Requirements
- Python 3.7+
- Linux/macOS (recommended)

### Known Limitations
- Systems with FIPS mode enabled will not allow MD5 python functions to execute.

### Dependencies
- Standard Python libraries

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/file-compare-utility.git

cd file-compare-utility
```

### Usage
```bash
python3 file-compare.py --file1 /path/to/file1 --file2 /path/to/file2
```

### Built-in help function
```bash
$: file-compare.py --help
usage: file-compare.py [-h] --file1 FILE1 --file2 FILE2 [--hash] [--size] [--compare] [--symlink]

Compare two files using several methods

options:
  -h, --help     show this help message and exit
  --file1 FILE1  Path to the first file
  --file2 FILE2  Path to the second file
  --hash         Output hash information
  --size         Output file size comparison
  --compare      Output file comparison results
  --symlink      Output symlink information

Example: python3 file-compare.py --file1 /path/to/file1 --file2 /path/to/file2 [--hash] [--size] [--compare] [--symlink]
```
