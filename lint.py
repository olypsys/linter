#
# A basic linting script for C++, Java, Kotlin and Swift files, specific to Olypsys Technologies Ltd.
#
# Copyright (c) 2024 Olypsys Technologies Ltd. All rights reserved.
#

import os
from datetime import date
from typing import Iterable
from enum import Enum
import re

rb = "\033[1;91m"
gb = "\033[1;92m"
pb = "\033[1;95m"
fe = "\033[0m"


class FileType(Enum):
    CPP = 1
    HPP = 2
    JAVA = 3
    KOTLIN = 4
    XML = 5
    SWIFT = 6


def _find_files_by_extension(
    folder_to_search: str,
    matching_extensions: Iterable[str],
    filepath_contains: Iterable[str] = None
) -> list[str]:
    """
    Find all files in the current folder with the given extensions
    matching_extensions: The extensions to match
    filepath_contains: Only return filepaths that contain at least one of the substrings specified in
    this array.
    """
    files = []
    for root, _, filenames in os.walk(folder_to_search):
        for filename in filenames:
            if not any([filename.endswith(ext) for ext in matching_extensions]):
                continue

            file_path = os.path.join(root, filename)
            if filepath_contains is not None:
                if all([x not in file_path for x in filepath_contains]):
                    continue
            files.append(file_path)
    return files


def find_cpp_files(folder_to_search: str) -> list[str]:
    return _find_files_by_extension(folder_to_search, {".cpp", ".hpp"}, {"buzzard/core", "buzzard/ui", "./tests/"})


def find_android_files(folder_to_search: str) -> list[str]:
    return _find_files_by_extension(folder_to_search, {".java", ".kt", ".ktx"})


def find_swift_files(folder_to_search: str) -> list[str]:
    return _find_files_by_extension(folder_to_search, {".swift"}, {"Olypsys/"})


def is_CamelCase(s: str) -> bool:
    is_all_lower = s != s.lower()
    is_all_upper = s != s.upper()
    has_underscores = "_" not in s

    if is_all_lower or is_all_upper or has_underscores:
        return False

    if s[0].islower():
        return False
    return True


def is_snake_case(s: str) -> bool:
    is_all_lower = s != s.lower()
    has_underscores = "_" in s

    if is_all_lower:
        if len(s) > 25:
            if has_underscores:
                return True
            else:
                return False
        return True
    return False


def get_file_type(file_path: str) -> FileType:
    if file_path.lower().endswith('.cpp') or file_path.lower().endswith('.cxx'):
        return FileType.CPP
    if file_path.lower().endswith('.hpp'):
        return FileType.HPP
    if file_path.lower().endswith('.java'):
        return FileType.JAVA
    if file_path.lower().endswith('.kt') or file_path.lower().endswith('.kts'):
        return FileType.KOTLIN
    if file_path.lower().endswith('.xml'):
        return FileType.XML
    if file_path.lower().endswith('.swift'):
        return FileType.SWIFT
    raise ValueError(f"Unknown file type for file {file_path}")


def check_file_path(file_path: str) -> int:
    # File should be CamelCase, with no spaces, underscores or dashes
    filename: str = os.path.basename(file_path)
    error_count = 0
    if filename != "main.cpp":
        if is_CamelCase(filename):
            print(f"{rb}Error, {filename}: File name should be CamelCase{fe}")
            error_count += 1
    if " " in filename or "_" in filename or "-" in filename:
        print(f"{rb}Error, {filename}: File name should not contain spaces, underscores or dashes{fe}")
        error_count += 1
    return error_count


def check_file(file_path: str, disable_line_length_checks: bool = True) -> int:
    filename: str = os.path.basename(file_path)
    file_type: FileType = get_file_type(file_path)
    error_count: int = 0
    error_count += check_file_path(file_path)
    character_brace_pattern = re.compile(r'[A-Za-z0-9]\{')

    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if not disable_line_length_checks:
                if len(line) > 100:
                    print(f"{rb}Error, {filename}:{i+1}: Line length >100{fe}")
                    error_count += 1

            if '\t' in line:
                print(f"{rb}Error, {filename}:{i+1}: Tab found{fe}")
                error_count += 1

            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith(' \n') or line.endswith(' \r'):
                print(f"{rb}Error, {filename}:{i+1}: Trailing whitespace found{fe}")
                error_count += 1

            # Check for m_ followed by an uppercase letter
            if "m_" in line and line.split("m_")[1][0].isupper():
                print(f"{rb}Error, {filename}:{i+1}: m_ followed by uppercase letter{fe}")
                error_count += 1

            # Check for namespace with brace on the same line
            if "namespace " in line and "{" in line:
                print(f"{rb}Error, {filename}:{i+1}: Namespace with brace on the same line{fe}")
                error_count += 1
            if "}; // namespace" in line:
                print(f"{rb}Error, {filename}:{i+1}: Extra semicolon{fe}")
                error_count += 1
            if " ;" in line:
                print(f"{rb}Error, {filename}:{i+1}: Extra space before semicolon{fe}")
                error_count += 1
            if file_type == FileType.CPP or file_type == FileType.HPP:
                if "struct " in line and "{" in line:
                    print(f"{rb}Error, {filename}:{i+1}: Struct with brace on the same line{fe}")
                    error_count += 1
                if "class " in line and "{" in line:
                    print(f"{rb}Error, {filename}:{i+1}: Class with brace on the same line{fe}")
                    error_count += 1
                if "enum class " in line and "{" in line:
                    print(f"{rb}Error, {filename}:{i+1}: Enum Class with brace on the same line{fe}")
                    error_count += 1
            if "}else" in line:
                print(f"{rb}Error, {filename}:{i+1}: " + "}else, should be newline" + f"{fe}")
                error_count += 1

            if file_type is FileType.KOTLIN or file_type is FileType.JAVA:
                # Check for commented import
                if line.strip().startswith("//import") or line.strip().startswith("// import"):
                    print(f"{rb}Error, {filename}:{i+1}: Commented import{fe}")
                    error_count += 1

            if file_type is FileType.KOTLIN or file_type is FileType.SWIFT:
                # Check that the line does not end with a ;
                if line.endswith(";"):
                    print(f"{rb}Error, {filename}:{i+1}: Line ends with ;{fe}")
                    error_count += 1
            if file_type is FileType.KOTLIN:
                if "func  " in line:
                    print(f"{rb}Error, {filename}:{i+1}: Extra space in function declaration{fe}")
                    error_count += 1
                if "if  " in line:
                    print(f"{rb}Error, {filename}:{i+1}: Extra space in if statement{fe}")
                    error_count += 1
                if "throw  " in line:
                    print(f"{rb}Error, {filename}:{i+1}: Extra space in throw statement{fe}")
                    error_count += 1
                if "let  " in line:
                    print(f"{rb}Error, {filename}:{i+1}: Extra space in let statement{fe}")
                    error_count += 1

            if "else{" in line:
                print(f"{rb}Error, {filename}:{i+1}: " + "else{, should be newline" + f"{fe}")
                error_count += 1
            if " if(" in line:
                print(f"{rb}Error, {filename}:{i+1}: if( should be if ({fe}")
                error_count += 1
            if " for(" in line:
                print(f"{rb}Error, {filename}:{i+1}: for( should be for ({fe}")
                error_count += 1
            if " while(" in line:
                print(f"{rb}Error, {filename}:{i+1}: while( should be while ({fe}")
                error_count += 1
            if " switch(" in line:
                print(f"{rb}Error, {filename}:{i+1}: switch( should be switch ({fe}")
                error_count += 1
            if file_type == FileType.CPP or file_type == FileType.HPP:
                if ") {" in line or "){" in line:
                    print(f"{rb}Error, {filename}:{i+1}:" + ") {" + f" should be broken with newline")
                    error_count += 1
            if file_type == FileType.JAVA or file_type == FileType.KOTLIN:
                if "){" in line:
                    print(f"{rb}Error, {filename}:{i+1}:" + "){" + f" should be broken with space")
                    error_count += 1
                if ")  {" in line:
                    print(f"{rb}Error, {filename}:{i+1}:" + ")  {" + f" should be broken with a single space")
                    error_count += 1
                if "let  {" in line:
                    print(f"{rb}Error, {filename}:{i+1}:" + "let {" + f" should be broken with a single space")
                    error_count += 1

            # Check for any alphanumeric character followed by a {
            if file_type == FileType.JAVA or file_type == FileType.KOTLIN or file_type == FileType.SWIFT:
                if character_brace_pattern.search(line):
                    print(f"{rb}Error, {filename}:{i+1}: Character followed by a brace{fe}")
                    error_count += 1


    # Load the file as string
    with open(file_path, 'r') as f:
        file_str = f.read()

    # Check for missing newline at end of file
    if len(file_str) > 0 and file_str[-1] != '\n':
        print(f"{rb}Error, {filename}: No newline at end of file{fe}")
        error_count += 1

    if "\n\n\n" in file_str:
        # Find the line number of the first occurrence of three consecutive newlines
        line_number = file_str.count("\n", 0, file_str.index("\n\n\n")) + 1
        print(f"{rb}Error, {filename} three consecutive newlines at line {line_number}{fe}")
        error_count += 1

    # Check for valid copyright header
    year = date.today().year

    is_cpp_tests_file = filename.startswith("Test") and file_type == FileType.CPP

    if is_cpp_tests_file:
        expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///"""
        )
        if not file_str.startswith(expected_header):
            print(f"{rb}Error, {filename}: Invalid copyright header{fe}")
            print("Expected: \n" + expected_header)
            print("\n\nActual: \n" + file_str[:len(expected_header)])
            error_count += 1
    if not is_cpp_tests_file and file_type == FileType.CPP:
        header_file_name = filename[:-4] + ".hpp"
        expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///
/// See {header_file_name} for documentation.
///"""
        )
        if filename == "main.cpp":
            expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///
/// \\file {filename}
///
/// \\brief"""
            )
        if not file_str.startswith(expected_header):
            print(f"{rb}Error, {filename}: Invalid copyright header{fe}")

            print("Expected: \n" + expected_header)
            print("\n\nActual: \n" + file_str[:len(expected_header)])
            error_count += 1
    if file_type == FileType.HPP:
        expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///
/// \\file {filename}
///
/// \\brief"""
        )
        if not file_str.startswith(expected_header):
            print(f"{rb}Error, {filename}: Invalid copyright header{fe}")

            print("Expected: \n" + expected_header)
            print("\n\nActual: \n" + file_str[:len(expected_header)])
            error_count += 1
    if file_type == FileType.JAVA or file_type == FileType.KOTLIN:
        expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///
/// This file is part of the Olypsys Android App.
///
"""
        )
        if not file_str.startswith(expected_header):
            print(f"{rb}Error, {filename}: Invalid copyright header{fe}")

            print("Expected: \n" + expected_header)
            print("\n\nActual: \n" + file_str[:len(expected_header)])
            error_count += 1
    if file_type == FileType.SWIFT:
        expected_header = (
f"""///
/// Copyright (c) {year} Olypsys Technologies Ltd. All rights reserved.
///
/// This file is part of the Olypsys iOS App.
///
"""
        )
        if not file_str.startswith(expected_header):
            print(f"{rb}Error, {filename}: Invalid copyright header{fe}")

            print("Expected: \n" + expected_header)
            print("\n\nActual: \n" + file_str[:len(expected_header)])
            error_count += 1

    return error_count


if __name__ == '__main__':

    # Is there a second argument - if so this is the file or folder to check
    import sys
    if len(sys.argv) > 1:
        to_check = sys.argv[1]
        # Is it a file or folder?
        if os.path.isdir(to_check):
            files = find_cpp_files(to_check) + find_android_files(to_check) + find_swift_files(to_check)
        else:
            files = [to_check]
    else:
        files = find_cpp_files(".") + find_android_files(".") + find_swift_files(".")
    n_files = len(files)
    error_count = 0
    for file in files:
        error_count += check_file(file)
    if error_count > 0:
        plural = ""
        if error_count > 1:
            plural = "s"
        print(f"{rb}{error_count} error{plural} found in {n_files} files.")

        exit(1)
    print(f"{gb}All {n_files} source files passed linting{fe}")
    exit(0)
