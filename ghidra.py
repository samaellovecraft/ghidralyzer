#!/usr/bin/env python3

import os
import argparse
import subprocess
import tempfile
import itertools as IT
from shutil import which

PROJECT_DIRECTORY = '/tmp'
GHIDRA_PATH = os.path.join(os.environ.get('LAB'), 'ghidra_11.0.3_PUBLIC/')

def uniquify(path, sep = ''):
    def name_sequence():
        count = IT.count()
        yield ''
        while True:
            yield '{s}_{n:d}'.format(s = sep, n = next(count))
    orig = tempfile._name_sequence
    with tempfile._once_lock:
        tempfile._name_sequence = name_sequence()
        path = os.path.normpath(path)
        dirname, basename = os.path.split(path)
        filename, ext = os.path.splitext(basename)
        fd, filename = tempfile.mkstemp(dir = dirname, prefix = filename, suffix = ext)
        os.close(fd)
        os.remove(filename)
        tempfile._name_sequence = orig
    return filename

def is_cancel_requested(platform):
    print('\033[32m' + 'Will run analysis in 3 seconds, press any key to cancel...' + '\033[0m')
    if platform == 'nt':
        from msvcrt import kbhit, getch
        from time import time
        start_time = time()
        while True:
            if kbhit():
                getch()
                return True
            elif (time() - start_time) >= 3:
                return False
    elif platform == 'posix':
        from select import select
        from sys import stdin
        i, _, _ = select( [stdin], [], [], 3 )
        return i

def main(filename, temp):
    if os.path.isdir(filename):
        return os.system(f'{GHIDRA_PATH}ghidraRun')
    if '.gpr' in filename:
        os.system(f'{GHIDRA_PATH}ghidraRun "{os.path.abspath(filename)}"')
        return
    if temp:
        proj_file = uniquify(os.path.join(PROJECT_DIRECTORY, os.path.basename(filename) + '.gpr'))
        out_dir = PROJECT_DIRECTORY
    else:
        proj_file = uniquify(filename + '.gpr')
        out_dir = os.path.dirname(filename)
        out_dir = out_dir if out_dir != '' else '.'
    proj_name = os.path.splitext(os.path.basename(proj_file))[0]

    match os.name:
        case 'nt':
            file_exe = which('file', path=r'C:\Program Files\Git\usr\bin')
        case _:
            file_exe = which('file')
    if file_exe:
        file_output = subprocess.check_output([file_exe, filename], shell=True).decode('utf8')
        print('\033[33m' + file_output + '\033[0m')

    should_run = not is_cancel_requested(os.name)
    if should_run:
        os.system(f'{GHIDRA_PATH}support/analyzeHeadless {out_dir} "{proj_name}" -import "{filename}"')
        os.system(f'{GHIDRA_PATH}ghidraRun "{proj_file}"')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to run Ghidra from the command line including automatic analysis and launching Ghidra for existing projects.')
    parser.add_argument('filename', type=str, help='target file or directory name')
    parser.add_argument('-t', '--temp', action='store_true', help='create a temporary project')

    args = parser.parse_args()
    main(args.filename, args.temp)
