import os
import subprocess
import argparse
import functions



# Parse the arguments given
parser = argparse.ArgumentParser("Compare the output of two different versions of (hi_)class")
parser.add_argument("input_file", type=str, help="Input file with values (or range of values) for each parameter")
parser.add_argument("class_v1", type=str, help="Folder with the first version of (hi_)class")
parser.add_argument("class_v2", type=str, help="Folder with the second version of (hi_)class")
args = parser.parse_args()

#Define directories:
#    BASE_DIR: this script;
#    CLASS_V1_DIR : first version of class to compare;
#    CLASS_V2_DIR : second version of class to compare;
#    INPUT_DIR : stores problematic ini files (and the current one)
#    OUTPUT_DIR : stores table with relative differences (and current output)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
CLASS_V1_DIR = BASE_DIR + args.class_v1
CLASS_V2_DIR = BASE_DIR + args.class_v2
INPUT_DIR = BASE_DIR + 'init_files/'
OUTPUT_DIR = BASE_DIR + 'output/'





#List of task that this code has to do:
#   1 - Import a file with the values/ranges of the parameters
#   2 - Generate a single ini file
#   3 - Run the two versions of class for the same ini file
#   4 - Compare the outputs
#   5 - Write a line in a table with the values of the parameters and the relative differences
#   6 - If the agreement is not good keep the ini file


#subprocess.call([CLASS_V1_DIR + 'class', INPUT_DIR + 'hi_class.ini'])