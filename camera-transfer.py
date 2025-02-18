#!/usr/bin/env python3

# Transfers data from one computer to another over SSH using SCP command

import logging              # For creating a log
import os                   # For copying files from one device to another
import shutil               # For removing a filled directory
import subprocess           # For remotely calling a script
from classes.sql_controller import SQLController  # For interacting with the DB

PI = 'pi@192.168.0.111'
CAMERA_DB = '/Users/Jordan/Developer/eds/capra-storage/capra-camera.db'
CAMERA_PATH = '/Users/Jordan/Developer/eds/capra-storage/'
# PROJECTOR_PATH = 'jordanrw@rlogin.cs.vt.edu:/home/ugrads/majors/jordanrw/capra-storage/'
PROJECTOR_PATH = PI + ':/home/pi/capra-storage/'


# Initialize the logger
def initialize_logger(path: str):
    logname = '{p}logs/camera-transfer.log'.format(p=path)
    logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# Deletes all directories that start with 'hike'
def delete_picture_directories(path: str):
    os.chdir(path)
    file_list = os.listdir(os.getcwd())
    for directory in file_list:
        try:
            if os.path.isdir(directory) and directory.startswith('hike'):
                shutil.rmtree(directory)
                logging.info('Removed {d}'.format(d=directory))
        except Exception as error:
            logging.exception('===== Error while trying to delete directory ===== ')
            logging.exception(error)


def main():
    initialize_logger(CAMERA_PATH)
    logging.info('Starting transfer script...')

    # 1. Copy all files from camera storage location to projector storage location
    # if a file being copied has the same name as a file already on the projector,
    # the old file will be overwritten
    logging.info('Begin SSH copy')
    try:
        os.system('scp -r {c}* {p}'.format(c=CAMERA_PATH, p=PROJECTOR_PATH))
    except Exception as error:
        logging.exception('===== Error while trying to copy data to projector ===== ')
        logging.exception(error)

    # 2. Remove all pictures on camera
    delete_picture_directories(CAMERA_PATH)

    # 3. Delete camera DB data
    # This removes all the data but does not drop tables (next indexes will be preseerved)
    sql_controller = SQLController(database=CAMERA_DB)
    sql_controller.delete_picture_and_hikes_tables()

    # 4. Start the remote script
    # subprocess.call('ssh pi@192.168.0.111 python3 /home/pi/capra/test-projector-insert.py', shell=True)
    
    # subprocess.call('ssh pi@192.168.0.111 export DISPLAY=:0', shell=True)
    subprocess.call('ssh pi@192.168.0.111 python3 /home/pi/Developer/capra-slideshow/slideshow-fade-image.py', shell=True)
    
    # subprocess.call('ssh pi@192.168.0.111 export DISPLAY=:0 && python3 /home/pi/Developer/capra-slideshow/slideshow-fade-image.py', shell=True)

    logging.info('...finished transfer script \n')


if __name__ == "__main__":
    main()
