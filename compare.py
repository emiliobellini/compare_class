import os
import subprocess
import functions

# Define directories:
#    BASE_DIR: this script;
#    CLASS_V1_DIR : first version of class to compare;
#    CLASS_V2_DIR : second version of class to compare;
#    INPUT_DIR : stores problematic ini files (and the current one)
#    OUTPUT_DIR : stores table with relative differences (and current output)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
CLASS_V1_DIR = BASE_DIR + '../hi_class_devel/'
CLASS_V2_DIR = BASE_DIR + '../hi_class_devel/'
INPUT_DIR = BASE_DIR + 'init_files/'
OUTPUT_DIR = BASE_DIR + 'output/'

#subprocess.call([CLASS_V1_DIR + 'class', INPUT_DIR + 'hi_class.ini'])