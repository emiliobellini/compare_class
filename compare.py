import os
import subprocess
import argparse
import functions as fs
import numpy as np



# Parse the given arguments
parser = argparse.ArgumentParser("Compare the output of two different versions of (hi_)class: class-v1, class-v2")
parser.add_argument("input_file", type=str, help="Input file with values (or range of values) for each parameter")
parser.add_argument("--p_class_v1", type=str, default = None, help="Input file with parameters only for class-v1")
parser.add_argument("--p_class_v2", type=str, default = None, help="Input file with parameters only for class-v2")
parser.add_argument("-N", type=int, default=1, help="Number of executions of the code (default = 1)")
parser.add_argument("--output_dir", "-o", type=str, default = None, help="Output folder")
args = parser.parse_args()



#Define working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'



#Read input file and generate two dictionaries containing the fixed and the varying parameters
fix_params, var_params = fs.read_ini_file(BASE_DIR + args.input_file)
#Read optional input file for class-v1 and generate a dictionary with its parameters
if args.p_class_v1 is None:
    params_class_v1 = {}
else:
    params_class_v1, _ = fs.read_ini_file(BASE_DIR + args.p_class_v1)
#Read optional input file for class-v1 and generate a dictionary with its parameters
if args.p_class_v2 is None:
    params_class_v2 = {}
else:
    params_class_v2, _ = fs.read_ini_file(BASE_DIR + args.p_class_v2)



#Define directories:
#    CLASS_V1_DIR : first version of class to compare;
#    CLASS_V2_DIR : second version of class to compare;
#    OUTPUT_DIR : stores the output files

CLASS_V1_DIR = BASE_DIR + fix_params['root_class_v1']
CLASS_V2_DIR = BASE_DIR + fix_params['root_class_v2']

if args.output_dir is None:
    OUTPUT_DIR = BASE_DIR + 'output/'
else:
    OUTPUT_DIR = BASE_DIR + args.output_dir



#Remove directories of class_v1 and class_v2 from the list of parameters
fix_params.pop('root_class_v1', None)
fix_params.pop('root_class_v2', None)



for i in np.arange(args.N):
    
    #Generate random values for all the varying parameters
    model_params = fs.generate_random(var_params)
    
    fs.group_parameters(fix_params, model_params)
    
#    print fix_params
#    print var_params


#List of task that this code has to do:
#   1 - Import a file with the values/ranges of the parameters
#   2 - Generate a single ini file
#   3 - Run the two versions of class for the same ini file
#   4 - Compare the outputs
#   5 - Write a line in a table with the values of the parameters and the relative differences
#   6 - If the agreement is not good keep the ini file


#subprocess.call([CLASS_V1_DIR + 'class', INPUT_DIR + 'hi_class.ini'])