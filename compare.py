import os
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
    
    #Initialize main dictionaries
    params = {}
    folders = {}
    output_data = {}
    output_diffs = {}
    
    #Read input parameters and output dictionaries
    #for them (keys: 'common', 'v1', 'v2')
    params = fs.read_input_parameters(args)
    
    #Get output path and name
    params = fs.get_output_path_and_name(params)
    
    #Create folder structure
    params, folders = fs.create_folders(args, params)
    
    #Generate ref output
    if args.ref:
        #Prepare params for ref models
        params = fs.prepare_ref_params(params)
    
        for v in ['ref_v1', 'ref_v2']:
            #Group parameters together for each version of class
            params[v] = fs.group_parameters(params[v])
    
            #Create ini files
            folders = fs.create_ini_file(params[v], folders, v)
    
            #Run class TODO: uncomment this
            fs.run_class(folders, v)
    
            #Read output and return a dictionary with data for each file
            for v in ['ref_v1', 'ref_v2']:
                try:
                    output_data[v] = fs.read_output(folders, v)
                except:
                    raise IOError('--------> No ref output found!')
    
    #Separate fixed params from the varying ones
    params = fs.separate_fix_from_varying(params)
    
    #Start loop
    for step in range(1,args.N+1):
    
        #Re-initialise output for v1 and v2
        output_data['v1'] = {}
        output_data['v2'] = {}
    
        #Only if has_output is 2 (both codes generated output)
        #exit the loop. Otherwise repeat the loop with new params.
        #TODO: reset to 0
        has_output = 0
        while has_output is not 2:
    
            #Generate random numbers for the varying parameters
            params = fs.generate_random_params(params)
    
            #Initialize has_output to 0.
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
        for v in ['v1', 'v2']:
            output_data[v] = fs.read_output(folders, v)
    
        #Initialize structure of output_diffs
        if not output_diffs:
            output_diffs = fs.get_output_diffs_struct(params, output_data)
        #Compare output
        fs.compare_output(params, output_data, args, output_diffs)
    
        #Remove tmp output files TODO: uncomment this
        # for file in os.listdir(folders['tmp']):
        #     os.remove(folders['tmp'] + file)
    
        #Print to screen the end of this iteration
        print 'Completed run ' + str(step) + ' of ' + str(args.N)
        sys.stdout.flush()
    
    #Write output
    fs.write_output_file(output_diffs, folders, args)
    
    #If requested, generate plots
    if args.want_plots:
        #File name and path
        fname = folders['main'] + folders['f_prefix'] + 'output.dat'
        #Read output table
        data_plots = fs.read_output_table(fname)
        #Generate plots
        fs.generate_plots(data_plots, folders['plots'])


    return









# import os, re
# import numpy as np
# import glob
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
