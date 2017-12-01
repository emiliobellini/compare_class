import sys
import functions as fs
import global_variables as gv


def run(args):
    """
    Main function. Steps:
      (i) Read the input parameters.
     (ii) Generate random values for the varying parameters
    (iii) Run the two versions of class and generate outputs
     (iv) Read the outputs and calculate the relative diffs
      (v) Output a table with the relative diffs for each model
     (vi) If requested, output plots with relative diffs for each variable
    """
    return









# import os, re
# import numpy as np
# import glob
# 
# #Files to compare, independent variables for each file and allowed percentage differences in the comparison
# COMPARED_FILES = ['background', 'cl', 'pk']
# INDEPENDENT_VARIABLES = {'background': 'z', 'cl': 'l', 'pk': 'k (h/Mpc)'}
# ALLOWED_PERCENTAGE_DIFFS = {'background': 1., 'cl': 1., 'pk': 1.}
# 
# 
# 
# 
# 
# #Define working directory
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
# 
# #Define dictionaries for the different versions of class
# class_v1 = {}
# class_v2 = {}
# class_v1['class_name'] = 'v1'
# class_v2['class_name'] = 'v2'
# 
# #Read input file and generate two dictionaries containing the fixed and the varying parameters
# fix_params, var_params = fs.read_ini_file(BASE_DIR + args.input_file)
# #Read optional input file for class-v1 and generate a dictionary with its parameters
# if args.p_class_v1 is None:
#     class_v1['params'] = {}
# else:
#     class_v1['params'], _ = fs.read_ini_file(BASE_DIR + args.p_class_v1)
# #Read optional input file for class-v1 and generate a dictionary with its parameters
# if args.p_class_v2 is None:
#     class_v2['params'] = {}
# else:
#     class_v2['params'], _ = fs.read_ini_file(BASE_DIR + args.p_class_v2)
# 
# 
# 
# #Define directories:
# #    class_v1['root'] : folder of the first version of class to compare;
# #    class_v2['root'] : folder of the second version of class to compare;
# #    OUTPUT_DIR : relative (to BASE_DIR) path where to store the output files
# 
# class_v1['root'] = BASE_DIR + fix_params['root_class_v1']
# class_v2['root'] = BASE_DIR + fix_params['root_class_v2']
# #Remove directories of class_v1 and class_v2 from the list of parameters
# fix_params.pop('root_class_v1', None)
# fix_params.pop('root_class_v2', None)
# 
# #Read the output directory
# if args.output_dir is None:
#     OUTPUT_DIR = 'output/'
# else:
#     OUTPUT_DIR = args.output_dir
# 
# #Folder containing all the problematic init files
# OUTPUT_PROBLEMATIC_INI = OUTPUT_DIR + 'problematic_ini/'
# #Folder containing the temporary output generated at each run
# OUTPUT_TMP = OUTPUT_DIR + 'tmp/'
# #Folder containing the plots
# OUTPUT_PLOTS = OUTPUT_DIR + 'plots/'
# 
# #Generate folder structure
# try:
#     os.mkdir(OUTPUT_DIR)
# except:
#     pass
# try:
#     os.mkdir(OUTPUT_PROBLEMATIC_INI)
# except:
#     pass
# try:
#     os.mkdir(OUTPUT_TMP)
# except:
#     pass
# if args.want_plots or args.want_only_plots:
#     try:
#         os.mkdir(OUTPUT_PLOTS)
#     except:
#         pass
# 
# 
# #Base name for the output files
# BASE_NAME = args.input_file.split('.')[0].split('/')[-1]
# 
# #Definition of the dictionaries containing the values of the input and output parameters
# input_params = {}
# output_params = {}
# 
# #Run only if needed
# if not args.want_only_plots:
#     for i in np.arange(args.N):
# 
# 
#         NO_OUTPUT = {}
#         NO_OUTPUT[class_v1['class_name']] = True
#         NO_OUTPUT[class_v2['class_name']] = True
#         root_output = {}
#         while any(NO_OUTPUT.values()):
#             #Generate random values for all the varying parameters
#             model_params = fs.generate_random(var_params)
# 
#             #Group parameters together to respect the (hi_)class syntax
#             common_params = fs.group_parameters(fix_params, model_params)
# 
#             #Cycle over the different versions of class to generate the ini file and execute class
#             for v in [class_v1, class_v2]:
#                 #Name and path of the new ini file
#                 v['ini_name'] = BASE_NAME + '_' + v['class_name']
#                 v['ini_path'] = BASE_DIR + OUTPUT_DIR + v['ini_name'] + '.ini'
#                 #Try to remove the file if already existing
#                 try:
#                     os.remove(v['ini_path'])
#                 except:
#                     pass
#                 #Create ini file for class and return the root where the output is stored
#                 root_output[v['class_name']] = fs.create_ini_file(v, common_params, OUTPUT_TMP)
#                 #Run class
#                 fs.run_class(v)
# 
#                 #Test if some output have been generated
#                 if glob.glob(root_output[v['class_name']] + '*') != []:
#                     NO_OUTPUT[v['class_name']] = False
# 
#             #If both outputs have been generated print on the screen the response
#             if not any(NO_OUTPUT.values()):
#                 print '----> Success! Output from both the (hi_)class versions'
#                 sys.stdout.flush()
#             #If no output has been generated print on the screen the response
#             if all(NO_OUTPUT.values()):
#                 print '--------> Both (hi_)class versions failed to run'
#                 sys.stdout.flush()
#             #If some output has been generated by only one version of class,
#             #delete it and restart the cycle
#             if any(NO_OUTPUT.values()):
#                 for file in os.listdir(OUTPUT_TMP):
#                     os.remove(OUTPUT_TMP + file)
#             if NO_OUTPUT[class_v1['class_name']] and not NO_OUTPUT[class_v2['class_name']]:
#                 print '--------> Only (hi_)class ' + str(class_v1['class_name']) + ' failed to run'
#                 sys.stdout.flush()
#             if NO_OUTPUT[class_v2['class_name']] and not NO_OUTPUT[class_v1['class_name']]:
#                 print '--------> Only (hi_)class ' + str(class_v2['class_name']) + ' failed to run'
#                 sys.stdout.flush()
# 
# 
#         #Construct the dictionary that stores all the input values
#         for k in model_params.keys():
#             if k in input_params.keys():
#                 input_params[k].append(model_params[k])
#             else:
#                 input_params[k] = [model_params[k]]
# 
#         #Find the common outputs of the two class runs
#         common_output = fs.find_common_output(class_v1, class_v2, COMPARED_FILES, os.listdir(OUTPUT_TMP))
# 
#         #Import the output for each version of class and store it in a dictionary
#         for v in [class_v1, class_v2]:
#             v['output'] = {}
#             fs.import_output(v, common_output, BASE_DIR + OUTPUT_TMP)
# 
#         #Initialise the variable that will contain the relative differences
#         percentage_diffs = {}
# 
#         #Calculate the max percentage difference for each variable of each file
#         for co in common_output:
#             #Determine what are the common dependent variables for each file
#             common_vars = [x for x in class_v1['output'][co] if x in class_v2['output'][co]]
#             common_vars = [x for x in common_vars if x != INDEPENDENT_VARIABLES[co]]
#             #Iterate over the common_vars to calculate the relative differences (except for the independent one)
#             for var in common_vars:
#                 percentage_diffs[co + ':' + var] = fs.return_max_percentage_diff(
#                 class_v1['output'][co][INDEPENDENT_VARIABLES[co]], class_v1['output'][co][var],
#                 class_v2['output'][co][INDEPENDENT_VARIABLES[co]], class_v2['output'][co][var])
# 
#         #Construct the dictionary that stores all the output values
#         for k in percentage_diffs.keys():
#             if k in output_params.keys():
#                 output_params[k].append(percentage_diffs[k])
#             else:
#                 output_params[k] = [percentage_diffs[k]]
# 
#         #Decides if the percentage differences are negligible or it has to store the ini file
#         KEEP_INI_FILES = False
#         for k in percentage_diffs.keys():
#             for co in common_output:
#                 if co in k:
#                     if percentage_diffs[k] > ALLOWED_PERCENTAGE_DIFFS[co]:
#                         KEEP_INI_FILES = True
#         #Move the file in the ini directory
#         if KEEP_INI_FILES:
#             for v in [class_v1, class_v2]:
#                 new_ini_path = BASE_DIR + OUTPUT_PROBLEMATIC_INI + v['ini_name'] + '_' + str(i+1) + '.ini'
#                 os.rename(v['ini_path'], new_ini_path)
# 
#         #Remove tmp output files
#         for file in os.listdir(OUTPUT_TMP):
#             os.remove(OUTPUT_TMP + file)
# 
#         #Print to screen the end of this iteration
#         print 'Completed run ' + str(i+1) + ' of ' + str(args.N)
#         sys.stdout.flush()
# 
# 
# 
# 
#     #Name for the output file
#     output_file = BASE_DIR + OUTPUT_DIR + BASE_NAME + '_output.dat'
# 
#     #Create an ordered list of parameters (before input and then output)
#     OUTPUT_ORDERED = input_params.keys() + output_params.keys()
# 
#     #Create array with values of OUTPUT_ORDERED
#     params = {}
#     params.update(input_params)
#     params.update(output_params)
# 
#     #Create output array
#     output_array = np.empty([len(params[OUTPUT_ORDERED[0]]), len(OUTPUT_ORDERED)])
#     for i in range(len(OUTPUT_ORDERED)):
#         for j in range(len(params[OUTPUT_ORDERED[i]])):
#             output_array[j][i] = params[OUTPUT_ORDERED[i]][j]
# 
#     #Write output file
#     with open(output_file, "w") as f:
#         f.write('#' + '       '.join(OUTPUT_ORDERED) + '\n')
#         np.savetxt(f, output_array, delimiter = '       ', fmt='%10.5e')
#     print 'Saved output table in ' + OUTPUT_DIR + BASE_NAME + '_output.dat'
#     sys.stdout.flush()
# 
# 
# 
#     #If plots wanted, generate them
#     if args.want_plots:
#         fs.generate_plots(output_params, BASE_DIR + OUTPUT_PLOTS + BASE_NAME)
#         print 'Saved figures in ' + OUTPUT_PLOTS + BASE_NAME + '_'
#         sys.stdout.flush()
# 
# #If only plots wanted, read the output files and generate them
# if args.want_only_plots:
#     data = np.loadtxt(OUTPUT_DIR + BASE_NAME + '_output.dat')
#     with open(OUTPUT_DIR + BASE_NAME + '_output.dat', "r") as f:
#         headers = f.readline()
#         headers = re.sub('#','',headers)
#         headers = headers.split('  ')
#         headers = [x for x in headers if x !='']
#         headers = [x for x in headers if x !=' ']
#         headers = [x.strip(' ') for x in headers]
#         headers = [x.strip() for x in headers]
#     for count in range(len(headers)):
#         if headers[count] not in var_params.keys():
#             output_params[headers[count]] = data.transpose()[count]
#             fs.generate_plots(output_params, BASE_DIR + OUTPUT_PLOTS + BASE_NAME)
# print 'Saved figures in ' + OUTPUT_PLOTS + BASE_NAME + '_'
# sys.stdout.flush()
# 

def info(args):
    return

# -----------------MAIN-CALL---------------------------------------------
if __name__ == '__main__':
    
    #Parse command-line arguments
    args = fs.argument_parser()
    
    if args.mode == 'run':
        sys.exit(run(args))
    elif args.mode == 'info':
        sys.exit(info(args))
