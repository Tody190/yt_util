# coding=utf-8
__author__ = 'yangtao'


import os
import re
import pprint




def replace_print(str_line):
    re_result = re.search("print +(?P<print_value>.+)", str_line)
    if re_result:
        new_print = "print(%s)"%re_result.group("print_value")
        new_str_line = str_line.replace(re_result.group(), new_print)

        return new_str_line


def check_print(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        if "print" in f.read():
            return True
        else:
            return False


def get_py2_files(py2_files_path):
    py2_files = []
    for root, dirs, files in os.walk(py2_files_path):
        for f in files:
            if f.endswith(".py"):
                py2_files.append(os.path.join(root, f))

    return py2_files


def start_conversion(path):
    py2_files = get_py2_files(path)

    for py2f in py2_files:
        if check_print(py2f):
            new_contents = ""
            with open(py2f, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    new_line = replace_print(line)
                    if new_line:
                        new_contents += new_line
                    else:
                        new_contents += line

            with open(py2f, "w", encoding="utf-8") as f:
                f.write(new_contents)


if __name__ == "__main__":
    py2_files_path = r"D:\mycode\file_packaging"
    start_conversion(py2_files_path)