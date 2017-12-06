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
    output_diff = {}
    output_diff_ref = {}
    
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
    
            #Run class
            fs.run_class(folders, v)
    
            #Read output and return a dictionary with data for each file
            try:
                output_data[v] = fs.read_output(folders, v)
            except:
                raise IOError('--------> No ref output found!')
    
    #Separate fixed params from the varying ones
    params = fs.separate_fix_from_varying(params)
    
    #Start loop
    for step in range(1, args.N+1):
    
        #Re-initialise output for v1 and v2
        output_data['v1'] = {}
        output_data['v2'] = {}
    
        #Only if has_output is 2 (both codes generated output)
        #exit the loop. Otherwise repeat the loop with new params.
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
    
        #Initialize structure of output_diff
        if not output_diff:
            output_diff = fs.get_output_diff_struct(params, output_data)
        #Compare output
        fs.compare_output(params, output_data, output_diff)
        #Compare reference and store in output_diff_ref
        if args.ref and not output_diff_ref:
            output_diff_ref = fs.get_output_diff_struct(params, output_data)
            fs.compare_output(params, output_data, output_diff_ref, mode='ref')
    
        #Remove tmp output files
        for file in os.listdir(folders['tmp']):
            os.remove(folders['tmp'] + file)
    
        #Print to screen the end of this iteration
        print 'Completed run ' + str(step) + ' of ' + str(args.N)
        sys.stdout.flush()
    
    #Write output
    output_path = fs.write_output_file(output_diff, folders)
    print 'Saved output table in ' + os.path.relpath(output_path)
    #Write output ref
    if args.ref:
        output_path = fs.write_output_file(output_diff_ref, folders, mode='ref')
        print 'Saved output ref table in ' + os.path.relpath(output_path)
    
    #If requested, generate plots
    if args.want_plots:
        #Read output table
        fname = folders['main'] + folders['f_prefix'] + 'output.dat'
        data_plots = fs.read_output_table(fname)
        #Read output table for ref
        fname = folders['main'] + folders['f_prefix'] + 'ref_output.dat'
        try:
            data_plots_ref = fs.read_output_table(fname)
        except:
            data_plots_ref = None
        #Generate plots
        fs.generate_plots(data_plots, data_plots_ref, folders['plots'])
        print 'Saved figures in ' + os.path.relpath(folders['plots'])
        sys.stdout.flush()
    
    #Clean output files and folders
    try:
        os.remove(folders['ini_ref_v1'])
        os.remove(folders['ini_ref_v2'])
    except:
        pass
    try:
        os.rmdir(folders['tmp'])
    except:
        pass
    try:
        os.rmdir(folders['ini_to_check'])
    except:
        pass


    return



def update(args):
    return


def info(args):
    """
    Given the output folder generate plots
    """
    
    #Output path
    output_path = fs.folder_exists_or(args.output_dir, mod='error')
    #Table path
    table_path = output_path + output_path.split('/')[-2] + '_output.dat'
    #Plots path
    plots_path = fs.folder_exists_or(output_path + 'plots/', mod='create')
    
    #Try to read output table, otherwise error
    try:
        data_plots = fs.read_output_table(table_path)
    except:
        raise IOError('--------> Output table not found!')
    
    #Generate plots
    fs.generate_plots(data_plots, plots_path)
    print 'Saved figures in ' + os.path.relpath(plots_path)
    sys.stdout.flush()

    
    return



# -----------------MAIN-CALL---------------------------------------------
if __name__ == '__main__':
    
    #Parse command-line arguments
    args = fs.argument_parser()
    
    if args.mode == 'run':
        sys.exit(run(args))
    if args.mode == 'update':
        sys.exit(run(args))
    elif args.mode == 'info':
        sys.exit(info(args))
