# -------------------------------------------------------------------------------------------------------------------------------
# Description: This Python script, converted from a shell script, creates an inotify watch on the specified directory and its 
# 	       subdirectories, monitoring the directories for when a file or directory is removed, modified, moved, or created. 
#              Events are logged in /var/log/watchfilesdlog
#
# Original shell script created using this tutorial: https://www.baeldung.com/linux/monitor-changes-directory-tree
#
# History:
#   DATE	    AUTHOR		COMMENT
#   06-06-2023  T. Vu		Converted shell script to python
#   06-07-2023  T. Vu       
# -------------------------------------------------------------------------------------------------------------------------------

import subprocess
import os
from datetime import datetime
import sys

def file_removed(directory, file):
    subprocess.call(['logger', '-i', '-t', 'watchfilesd', '-p', 'local0.info', f'{file} was removed from {directory}'])

def file_modified(directory, file):
    subprocess.call(['logger', '-i', '-t', 'watchfilesd', '-p', 'local0.info', f'The file {directory}{file} was modified'])

def file_created(directory, file):
    subprocess.call(['logger', '-i', '-t', 'watchfilesd', '-p', 'local0.info', f'The file {directory}{file} was created'])

def file_moved_to(directory, file):
    subprocess.call(['logger', '-i', '-t', 'watchfilesd', '-p', 'local0.info', f'{file} was moved to {directory}'])

def process_file(directory, file):
    fullpath = os.path.join(directory, file)

    # If 'file' is a directory, iterate recursively over the directory contents
    if os.path.isdir(fullpath):
        for dirpath, subdirectories, files in os.walk(fullpath):
            for filename in files:
                filepath = os.path.join(dirpath, filename)
                print(f"Pre-staging {filepath}")

                # Append a message to the file
                file_obj = open(filepath, "")
                file_obj.write("PRE-STAGED\n")
                file_obj.close()

# .status hidden file does not have group write permissions

                # Make a status file for each file to indicate it has been processed
                status_file = "." + filename + "status"
                status_path = os.path.join(dirpath, status_file)
                with open(status_path, 'w') as status:
                    status.write(f"{datetime.now()}: Pre-staged\n")
                    # Make the file hidden
                    # subprocess.check_call(["attrib","+H", status_path])
                    # The creation of the status file should create a log in /var/log/watchfilesdlog by nature of inotifywatch


    # If 'file' is just a file, perform the process


def main():
    try:
        # Enter the path to the desired directory to watch relative to the script's directory
        # The directory of the script being run is os.path.dirname(os.path.abspath(__file__))
        directory_to_watch = os.path.dirname(os.path.abspath(__file__)) + "/" + sys.argv[1]
    except:
        # If no argument passed
        directory_to_watch = os.path.dirname(os.path.abspath(__file__))

    print(f"Watching {directory_to_watch}")

    process = subprocess.Popen(['inotifywait', '-q', '-m', '-r', '-e', 'modify,delete,create,moved_to', directory_to_watch],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in process.stdout:
        tokens = line.decode().split()
        directory = tokens[0]
        event = tokens[1]
        file = tokens[2]

        if event.startswith('MODIFY'):
            file_modified(directory, file)
        elif event.startswith('CREATE'):
            file_created(directory, file)
        elif event.startswith('DELETE'):
            file_removed(directory, file)
        elif event.startswith('MOVED_TO'):
            file_moved_to(directory, file)
            process_file(directory, file)


if __name__ == '__main__':
    main()

