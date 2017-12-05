import sys
import functions as fs
import global_variables as gv


def run(args):
    """
    Main function. The main steps are:
      (i) Read the input parameters.
     (ii) Generate random values for the varying parameters
    (iii) Run the two versions of class and generate outputs
     (iv) Read the outputs and calculate the relative diffs
      (v) Output a table with the relative diffs for each model
     (vi) Optional: output plots with relative diffs for each variable
    
    Loop over points (ii)-(iv) to sample different models
    """
    
    #Read input parameters and output dictionaries
    #for them (keys: 'common', 'v1', 'v2')
    params = fs.read_input_parameters(args)
    
    #Get output path and name
    params = fs.get_output_path_and_name(params)
    
    #Create folder structure
    params, folders = fs.create_folders(args, params)
    
    #Separate fixed params from the varying ones
    params = fs.separate_fix_from_varying(params)
    
    #Start loop
    for step in range(1,args.N+1):
        
        #Only if has_output is 2 (both codes generated output)
        #exit the loop. Otherwise repeat the loop with new params.
        #TODO: reset to 0
        has_output = 2
        while has_output is not 2:
            #Generate random numbers for the varying parameters
            params = fs.generate_random_params(params)
            
            #Initialize output to 0.
            has_output = 0
            for v in ['v1', 'v2']:
                #Group parameters together for each version of class
                params[v] = fs.group_parameters(params[v])
                
                #Create ini files
                folders = fs.create_ini_file(params[v], folders, v)
                
                #Run class
                fs.run_class(folders, v)
                
                #Check if run_class generated output
                has_output = fs.has_output(folders, v, has_output)
            
            #Print messages and store ini files depending on has_output
            fs.print_messages(has_output)
            
            #Clean ini files. If only one output has been generated,
            #store the ini files in ini_to_check/.
            fs.clean_ini(step, folders, has_output)
        
        #Read output and return a dictionary with data for each file
        output = fs.read_output(folders)


#    print params
#    print folders
#    print output
    
    
    return









# import os, re
# import numpy as np
# import glob
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
