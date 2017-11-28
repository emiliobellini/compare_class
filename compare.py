import os, sys
import argparse
import numpy as np
import functions as fs

#Files to compare and independent variables for each file
COMPARED_FILES = ['background', 'cl', 'pk']
INDEPENDENT_VARIABLES = {'background': 'z', 'cl': 'l', 'pk': 'k (h/Mpc)'}


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

#Define dictionaries for the different versions of class
class_v1 = {}
class_v2 = {}
class_v1['class_name'] = 'v1'
class_v2['class_name'] = 'v2'

#Read input file and generate two dictionaries containing the fixed and the varying parameters
fix_params, var_params = fs.read_ini_file(BASE_DIR + args.input_file)
#Read optional input file for class-v1 and generate a dictionary with its parameters
if args.p_class_v1 is None:
    class_v1['params'] = {}
else:
    class_v1['params'], _ = fs.read_ini_file(BASE_DIR + args.p_class_v1)
#Read optional input file for class-v1 and generate a dictionary with its parameters
if args.p_class_v2 is None:
    class_v2['params'] = {}
else:
    class_v2['params'], _ = fs.read_ini_file(BASE_DIR + args.p_class_v2)



#Define directories:
#    class_v1['root'] : folder of the first version of class to compare;
#    class_v2['root'] : folder of the second version of class to compare;
#    OUTPUT_DIR : relative (to BASE_DIR) path where to store the output files

class_v1['root'] = BASE_DIR + fix_params['root_class_v1']
class_v2['root'] = BASE_DIR + fix_params['root_class_v2']
#Remove directories of class_v1 and class_v2 from the list of parameters
fix_params.pop('root_class_v1', None)
fix_params.pop('root_class_v2', None)

#Read the output directory
if args.output_dir is None:
    OUTPUT_DIR = 'output/'
else:
    OUTPUT_DIR = args.output_dir

#Folder containing all the problematic init files
OUTPUT_PROBLEMATIC_INI = OUTPUT_DIR + 'problematic_ini/'
#Folder containing the temporary output generated at each run
OUTPUT_TMP = OUTPUT_DIR + 'tmp/'

#Generate folder structure
try:
    os.mkdir(OUTPUT_DIR)
except:
    pass
try:
    os.mkdir(OUTPUT_PROBLEMATIC_INI)
except:
    pass
try:
    os.mkdir(OUTPUT_TMP)
except:
    pass






for i in np.arange(args.N):

    #Generate random values for all the varying parameters
    model_params = fs.generate_random(var_params)

    #Group parameters together to respect the (hi_)class syntax
    common_params = fs.group_parameters(fix_params, model_params)



    #Cycle over the different versions of class to generate the ini file and execute class
    for v in [class_v1, class_v2]:
        #Name and path of the new ini file
        v['ini_name'] = args.input_file.split('.')[0] + '_' + v['class_name']
        v['ini_path'] = BASE_DIR + OUTPUT_DIR + v['ini_name'] + '.ini'
        #Try to remove the file if already existing
        try:
            os.remove(v['ini_path'])
        except:
            pass
        #Create ini file for class
        fs.create_ini_file(v, common_params, OUTPUT_TMP)
        #Run class (TODO: uncomment the following line)
        #fs.run_class(v)
    
    #Find the common outputs of the two class runs
    common_output = fs.find_common_output(class_v1, class_v2, COMPARED_FILES, os.listdir(OUTPUT_TMP))
    
    #Import the output for each version of class and store it in a dictionary
    for v in [class_v1, class_v2]:
        v['output'] = {}
        fs.import_output(v, common_output, OUTPUT_TMP)
    
    #Initialise the variable that will contain the relative differences
    percentage_diffs = {}
    
    #Calculate the max percentage difference for each variable of each file
    for co in common_output:
        percentage_diffs[co] = {}
        #Determine what are the common dependent variables for each file
        common_vars = [x for x in class_v1['output'][co] if x in class_v2['output'][co]]
        common_vars = [x for x in common_vars if x != INDEPENDENT_VARIABLES[co]]
        #Iterate over the common_vars to calculate the relative differences (except for the independent one)
        for var in common_vars:
            percentage_diffs[co][var] = fs.return_max_percentage_diff(
            class_v1['output'][co][INDEPENDENT_VARIABLES[co]], class_v1['output'][co][var], 
            class_v2['output'][co][INDEPENDENT_VARIABLES[co]], class_v2['output'][co][var])

#    print percentage_diffs



#List of task that this code has to do:
#   5 - Write a line in a table with the values of the parameters and the relative differences
#   6 - If the agreement is not good keep the ini file



sys.exit()