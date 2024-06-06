#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from subprocess import check_output
from shutil import which

GHIDRA_PATH = '/usr/share/ghidra' # CHANGE THIS

OS = os.name
if OS == 'nt':
    TEMP_DIR = os.environ.get('TMP')
elif OS == 'posix':
    TEMP_DIR = '/tmp'

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'

def colorecho(clr, msg):
    print(clr + msg + '\033[0m')

def uniquify(path):
    dirname, basename = os.path.split(path)
    filename, ext = os.path.splitext(basename)
    uniq_path = path
    count = 0
    while os.path.exists(uniq_path):
        uniq_path = os.path.join(dirname, f'{filename}.{count}{ext}')
        count += 1
    return uniq_path

def is_cancel_requested(platform, timeout=3):
    colorecho(GREEN, f'Analysis will start in {timeout} seconds. Press any key to cancel...')
    if platform == 'nt':
        from msvcrt import kbhit, getch
        from time import time
        start_time = time()
        while True:
            if kbhit():
                getch()
                return True
            elif (time() - start_time) >= timeout:
                return False
    elif platform == 'posix':
        from select import select
        from sys import stdin
        i, _, _ = select([stdin], [], [], timeout)
        return i

def print_file_type(filename, platform):
    if platform == 'nt':
        file_exe = which('file', path=r'C:\Program Files\Git\usr\bin')
    elif platform == 'posix':
        file_exe = which('file')
    if file_exe:
        colorecho(BLUE, check_output([file_exe, filename]).decode('utf8'))
    else:
        colorecho(RED, 'The file utility was not found on the system!')

def launch_ghidra(proj_file=None):
    msg = 'Launching Ghidra...'
    command = f'{GHIDRA_PATH}/ghidraRun'
    if proj_file:
        msg = 'Loading the project...'
        command += f' "{proj_file}"'
    colorecho(GREEN, msg)
    os.system(command)

def prepare_project(target_path, temp=None):
    if temp:
        proj_file = uniquify(os.path.join(TEMP_DIR, os.path.basename(target_path) + '.gpr'))
        proj_location = TEMP_DIR
    else:
        proj_file = uniquify(target_path + '.gpr')
        proj_location = os.path.dirname(target_path)
        proj_location = proj_location if proj_location != '' else '.'
    proj_name = os.path.splitext(os.path.basename(proj_file))[0]
    return proj_name, proj_location, proj_file

def main(target_path, temp):
    print_file_type(target_path, OS)
    target_path = os.path.abspath(os.path.normpath(target_path))

    if os.path.isdir(target_path):
        # TODO: implement bulk import
        colorecho(RED, 'The target path is not a project file nor a binary!')
        response = input('Launch Ghidra anyway? [Y/n] ').strip().lower() or 'y'
        if response.startswith('y'):
            return launch_ghidra()
        return
    if '.gpr' in target_path:
        return launch_ghidra(target_path)

    proj_name, proj_location, proj_file = prepare_project(target_path, temp)

    should_run = not is_cancel_requested(OS)
    if should_run:
        os.system(f'{GHIDRA_PATH}/support/analyzeHeadless {proj_location} "{proj_name}" -import "{target_path}"')
        colorecho(BLUE, f'Analysis completed. Created project: {proj_file}')
        launch_ghidra(proj_file)


if __name__ == '__main__':
    parser = ArgumentParser(description='ghidralyzer is a script that automates the process of creating a project, importing and analyzing a binary in Ghidra from the command line. If the provided target is a project file (.gpr), it will simply load the existing project.')
    parser.add_argument('target_path', type=str, help='path to the target binary or project file')
    parser.add_argument('-t', '--temp', action='store_true', help='create a temporary project in the TEMP_DIR')

    args = parser.parse_args()
    main(args.target_path, args.temp)
