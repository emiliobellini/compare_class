#This module contains all the functions needed by the compare.py module.
import os
import re
import sys
import shutil
import argparse
import random
import subprocess
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import global_variables as gv


def argument_parser():
    """ Parse the command-line arguments

    Returns:
        a class with the given arguments

    """
    
    parser = argparse.ArgumentParser(
    'Compare the output of two different versions of (hi_)class. Useful to:\n'
    ' (i) check that a new version of the code does not introduce new bugs;\n'
    '(ii) check the differences introduced varying the precision parameters.\n'
    )
    
    #Add supbarser to select between run and info modes.
    subparsers = parser.add_subparsers(dest='mode',
    help='Either "run", to run the sampler and optionally generate '
    'the plots, or "info", to just generate the plots.')
    
    run_parser = subparsers.add_parser('run')
    update_parser = subparsers.add_parser('update')
    info_parser = subparsers.add_parser('info')
    
    #Arguments for 'run'
    run_parser.add_argument('input_file', type=str, help='Input file')
    run_parser.add_argument('--params-v1', type=str, default = None,
    help='Input file only for class-v1')
    run_parser.add_argument('--params-v2', type=str, default = None,
    help='Input file only for class-v2')
    run_parser.add_argument('--ref', type=str, default = None,
    help='Reference ini file')
    run_parser.add_argument('-N', type=int, default=2,
    help='Number of iterations (default = 1)')
    run_parser.add_argument('--want-plots', action='store_true',
    help='Generate plots from the output')
    
    #Arguments for update
    update_parser.add_argument('input_file', type=str, help='Input file')
    update_parser.add_argument('output_dir', type=str,
    help='Folder where the output is stored')
    update_parser.add_argument('--params-v1', type=str, default = None,
    help='Input file only for class-v1')
    update_parser.add_argument('--params-v2', type=str, default = None,
    help='Input file only for class-v2')
    update_parser.add_argument('--ref', type=str, default = None,
    help='Reference ini file')
    update_parser.add_argument('--want-plots', action='store_true',
    help='Generate plots from the output')

    #Arguments for 'info'
    info_parser.add_argument('output_dir', type=str,
    help='Folder where the output is stored')

    args = parser.parse_args()
    
    return args


def read_input_parameters(args):
    """
    Read the input parameters.
    
    Return a dict with the parameters (keys: 'common', 'v1', 'v2', 'ref').
    """
    
    #Define the main dictionary params
    params = {}
    
    #Define different dictionaries for parameters
    params['common'] = {}
    params['v1'] = {}
    params['v2'] = {}
    if args.ref:
        params['ref_v1'] = {}
        params['ref_v2'] = {}
    
    #Read the common parameters
    params['common'] = read_ini_file(args.input_file)
    
    #Read parameters for class_v1
    if args.params_v1:
        params['v1'] = read_ini_file(args.params_v1)
    
    #Read parameters for class_v2
    if args.params_v2:
        params['v2'] = read_ini_file(args.params_v2)
    
    #Read parameters for reference model
    if args.ref:
        params['ref_v1'] = read_ini_file(args.ref)
        params['ref_v2'] = read_ini_file(args.ref)

    return params


def read_ini_file(fname):
    """
    Open and read an imput file.
    
    Return a dict with the parameters in that file.
    """
    
    #Initialise dict
    params = {}
    
    #Check if file exists and return its absolute path
    path_file = os.path.abspath(fname)
    if not os.path.exists(path_file):
        raise IOError('The file ' + fname + ' does not exist!')
    
    #Read each line of the file
    with open(path_file, "r") as f:
        for line in f:
            #Remove comments
            line = re.sub('#.+', '', line)
            if '=' in line:
                #Separate keys from values
                (key, val) = line.split('=')
                #Remove white spaces
                key = key.strip()
                val = val.strip()
                #Assign to dict key and value
                params[key] = val
    
    return params


def get_output_path_and_name(params):
    """
    Extract from the params dict the output path and the prefix
    for all the output files.
    
    Return the params dict with the output folder split into
    'root' and 'f_prefix'.
    """
    
    #Extract the output folder and file prefix from params
    if 'root_output' in params['common'].keys():
        params['root'] = params['common']['root_output'].split('/')
        params['f_prefix'] = params['root'][-1]
        params['root'] = '/'.join(params['root'][:-1]) + '/'
    else:
        raise IOError('No root_output in the parameter file')
    
    #Remove the old 'root_output' key from params
    params['common'].pop('root_output', None)
    
    return params


def folder_exists_or(fname, mod = 'error'):
    """
    Check if a folder exists.
    If it exists return the absolute path,
    otherwise raise an error or create it
    (depending on the mode)
    """

    #Absolute path of the folder
    abs_path = os.path.abspath(fname) + '/'

    #Check if file exists
    if not os.path.isdir(abs_path):
        if mod == 'create':
            os.makedirs(abs_path)
        else:
            raise IOError(abs_path + 'does not exist!')

    return abs_path


def create_folders(args, params):
    """
    Create folder structure.

    Return a dict with the folders created.
    In addition it removes from params the root keys
    """

    #Define folders dict
    folders = {}
    
    #Create key for the file prefix
    folders['f_prefix'] = params['f_prefix']

    #Create output folder
    fname = params['root']
    folders['main'] = folder_exists_or(fname, 'create')

    #Extract installation folders of class_v1 and class_v2
    fname = params['common']['root_class_v1']
    folders['v1'] = folder_exists_or(fname, 'error')
    if args.ref:
        folders['ref_v1'] = folders['v1']
    fname = params['common']['root_class_v2']
    folders['v2'] = folder_exists_or(fname, 'error')
    if args.ref:
        folders['ref_v2'] = folders['v2']

    #Create tmp folder (for class output)
    fname = folders['main'] + 'tmp/'
    folders['tmp'] = folder_exists_or(fname, 'create')

    #Create ini_to_check folder (for ini files that generated
    #output from one version of (hi_)class only)
    fname = folders['main'] + 'ini_to_check/'
    folders['ini_to_check'] = folder_exists_or(fname, 'create')

    #Create plot folder folder (for class output)
    if args.want_plots:
        fname = folders['main'] + 'plots/'
        folders['plots'] = folder_exists_or(fname, 'create')
    
    #Create input folder and store input files
    fname = folders['main'] + 'input_files/'
    folders['input_files'] = folder_exists_or(fname, 'create')
    fold = os.path.abspath('.') + '/' + args.input_file
    fnew = folders['input_files'] + args.input_file.split('/')[-1]
    shutil.copy2(fold, fnew)
    if args.params_v1:
        fold = os.path.abspath('.') + '/' + args.params_v1
        fnew = folders['input_files'] + args.params_v1.split('/')[-1]
        shutil.copy2(fold, fnew)
    if args.params_v2:
        fold = os.path.abspath('.') + '/' + args.params_v2
        fnew = folders['input_files'] + args.params_v2.split('/')[-1]
        shutil.copy2(fold, fnew)
    if args.ref:
        fold = os.path.abspath('.') + '/' + args.ref
        fnew = folders['input_files'] + args.ref.split('/')[-1]
        shutil.copy2(fold, fnew)
    
    #Assign to params of each version of class the relative path of
    #the tmp folder, which will be used by class to store the outputs
    fname = os.path.relpath(folders['tmp']) + '/' + folders['f_prefix']
    params['v1']['root'] = fname + 'v1_'
    params['v2']['root'] = fname + 'v2_'
    if args.ref:
        params['ref_v1']['root'] = fname + 'ref_v1_'
        params['ref_v2']['root'] = fname + 'ref_v2_'

    #Remove roots from params
    params.pop('f_prefix', None)
    params.pop('root', None)
    params['common'].pop('root_class_v1', None)
    params['common'].pop('root_class_v2', None)
   
    return params, folders


def prepare_ref_params(params):
    """
    Prepare params for reference models
    """
    
    #Extract params from common
    for k in params['common']:
        if k not in params['ref_v1']:
            params['ref_v1'][k] = params['common'][k]
        if k not in params['ref_v2']:
            params['ref_v2'][k] = params['common'][k]
    #Extract params from v1
    for k in params['v1']:
        if k not in params['ref_v1']:
            params['ref_v1'][k] = params['v1'][k]
    #Extract params from v2
    for k in params['v2']:
        if k not in params['ref_v2']:
            params['ref_v2'][k] = params['v2'][k]
    
    #Remove params with value None
    for k in params['ref_v1'].keys():
        if 'None' in params['ref_v1'][k]:
            params['ref_v1'].pop(k, None)
    for k in params['ref_v2'].keys():
        if 'None' in params['ref_v2'][k]:
            params['ref_v2'].pop(k, None)
    
    return params


def separate_fix_from_varying(params):
    """
    Restructure the params dict.
    
    Divide the 'common' params into fixed and varying.
    Fixed params are copied in both 'v1' and 'v2'.
    Varying are copied in 'var'. 'common' is removed.
    """
    
    #Initialize key var, where all the varying params
    #are stored.
    params['var'] = {}
    #For each key, if it is a range move it to 'var'
    for key in params['common']:
        val = params['common'][key].split(',')
        if len(val) == 2:
            try:
                float(val[0].strip())
                float(val[1].strip())
                
                params['var'][key] = params['common'][key]
            except:
                pass
    
    #Remove the varying keys from 'common'
    for key in params['var'].keys():
        params['common'].pop(key, None)
    
    #Copy fixed keys from 'common' to 'v1' and 'v2'
    for key in params['common'].keys():
        params['v1'][key] = params['common'][key]
        params['v2'][key] = params['common'][key]
    
    #Remove the 'common' key
    params.pop('common', None)
    
    return params


def generate_random_params(params):
    """
    Return the params dict with random values
    instead of ranges.
    """
    
    for key in params['var']:
        val = params['var'][key].split(',')
        xmin = float(val[0].strip())
        xmax = float(val[1].strip())
        rnd = random.uniform(xmin, xmax)
        params['v1'][key] = rnd
        params['v2'][key] = rnd
    
    return params


def group_parameters(params):
    """
    Group params together to respect the
    (hi_)class syntax.
    
    Return an updated dict of params.
    """
    
    #Find keys that end with __1
    new_keys = []
    for key in params.keys():
        if '__1' in key:
            new_keys.append(key.strip('__1'))
    
    for new_key in new_keys:
        count=0
        new_val = ''
        for key in params.keys():
            if new_key + '__' in key:
                count += 1
        for i in range(count):
            old_key = new_key + '__' + str(i+1)
            new_val += str(params[old_key]) + ','
        new_val = new_val[:-1]
        params[new_key] = new_val
    
    return params


def create_ini_file(params, folders, v):
    """
    Create ini file for each version of class
    and write it in the output folder.
    Store the ini path in folders.
    """
    
    ini_path = folders['main'] + folders['f_prefix'] + v + '.ini'
    #Create ini file
    with open(ini_path, 'w') as f:
        for k in params.keys():
            if '__' not in k:
                f.write(str(k) + ' = ' + str(params[k]) + '\n')
    
    #Store ini path
    folders['ini_' + v] = ini_path

    return folders


def run_class(folders, v):
    """
    Run the current version of class
    """
    #Get the path to class
    class_path = folders[v] + 'class'
    #Run class
    subprocess.call([class_path, folders['ini_' + v]])
    
    return


def has_output(folders, v, output):
    """
    Check if run_class generated the requested output
    and return True or False
    """
    
    #File name to match to check if output was generated
    fname = folders['f_prefix'] + v + '*'
    #List of files matching the pattern fname
    match = fnmatch.filter(os.listdir(folders['tmp']), fname)
    #Add to output 1 if the list is not empty
    if match:
        output = output + 1
    
    return output


def print_messages(output):
    """
    Print messages about the status of the previous run.
    """
    
    #If no output print message
    if output is 0:
        print '--------> Both (hi_)class versions failed to run'
        sys.stdout.flush()
    #If one output print message and store ini files
    elif output is 1:
        print '--------> Only one version of (hi_)class run'
        sys.stdout.flush()
    #If both output print message
    elif output is 2:
        print '----> Success! Output from both the (hi_)class versions'
        sys.stdout.flush()
    
    return


def clean_ini(step, folders, output):
    """
    If only one version of (hi_)class generated output
    store the ini files in the ini_to_check/ folder,
    otherwise delete them.
    """
    
    #Define folders
    main = folders['main']
    ini = folders['ini_to_check']
    
    for v in ['ini_v1', 'ini_v2']:
        #If one output store ini files
        if output is 1:
            new_ini = re.sub(main, '', folders[v])
            new_ini = re.sub('.ini', '_' + str(step) + '.ini', new_ini)
            new_ini = ini + new_ini
            os.rename(folders[v], new_ini)
        else:
            os.remove(folders[v])
    
    return


def read_output(folders, v):
    """
    Read output files and return a dictionary with
    the variables for each file.
    """
    
    output_data = {}
    #Common prefix for all the outputs
    common = folders['tmp'] + folders['f_prefix']
    #Create dictionary for each output of class
    for k in gv.X_VARS.keys():
        try:
            out = common + v + '_' + k + '.dat'
            output_data[k] = read_output_file(out, k)
        except:
            pass
    
    return output_data


def read_output_file(path, loc):
    """
    Given the path of a file read the necessary columns
    and store the values in a dictionary
    """
    
    #Define dict that contains the output
    output_data = {}
    #Get headers
    headers = get_headers(path, loc)
    #Get content
    content = np.genfromtxt(path).transpose()
    #Create dictionaries with keys that are both in the
    #output and X_VARS or Y_VARS
    for h in gv.X_VARS[loc]:
        col = headers.index(h)
        output_data[h] = content[col]
    for h in gv.Y_VARS[loc]:
        try:
            col = headers.index(h)
            output_data[h] = content[col]
        except:
            pass
    
    return output_data

def get_headers(path, loc):
    """
    Given a file path, get the headers of that file
    """
    
    with open(path, 'r') as f:
        headers = f.read().splitlines()
    headers = [x for x in headers if x[0] == '#']
    headers = headers[-1]
    headers = re.sub('#','',headers)
    headers = re.split('\d+:', headers)
    headers = [x.strip() for x in headers]
    headers = [x for x in headers if x !='']
    try:
        headers = [sub_dict(x, gv.DICTIONARY[loc]) for x in headers]
    except:
        pass
    
    return headers


def sub_dict(txt, rules):
    """
    Given a string, substitute the rules contained
    in dict.
    """
    
    rep = dict((re.escape(k), v) for k, v in rules.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], txt)
    
    return text


def get_output_diffs_struct(params, output_data):
    """
    Return a dictionary with the same structure
    of output_data[v]
    """
    
    #Initialize dict
    output_diffs = {}
    
    #Create input keys
    output_diffs['input_params'] = {}
    for var in params['var'].keys():
        output_diffs['input_params'][var] = []
    
    #Create output keys
    for k in output_data['v1'].keys():
        output_diffs[k] = {}
        for var in output_data['v1'][k].keys():
            if var in gv.Y_VARS[k]:
                output_diffs[k][var] = []
    
    
    return output_diffs

def compare_output(params, output_data, args, output_diffs):
    """
    Given the output return the dictionary
    with the max percentage diff for each
    dependent variable
    """
    #Initialize rel_diff key
    output_data['rel_diff'] = {}
    
    #Define list of files
    files = output_data['v1'].keys()
    #Iterate over the various files
    for f in files:
        output_data['rel_diff'][f] = {}
        #Define dependent keys for each file
        keys = output_data['v1'][f].keys()
        keys = [x for x in keys if x in gv.Y_VARS[f]]
        for k in keys:
            #Define (x, y) vars for class_v1
            x1 = output_data['v1'][f][gv.X_VARS[f]]
            y1 = output_data['v1'][f][k]
            #Define (x, y) vars for class_v2
            x2 = output_data['v2'][f][gv.X_VARS[f]]
            y2 = output_data['v2'][f][k]
            #If ref models calculate (x, y) of them
            try:
                #Define (x, y) vars for reference class_v1
                ref_x1 = output_data['ref_v1'][f][gv.X_VARS[f]]
                ref_y1 = output_data['ref_v1'][f][k]
                #Define (x, y) vars for reference class_v2
                ref_x2 = output_data['ref_v2'][f][gv.X_VARS[f]]
                ref_y2 = output_data['ref_v2'][f][k]
            except:
                #If ref is not specified or does not have the
                #requested key, assign to both refs (x1, y1).
                #Iin this way the relative diff will be 0.
                ref_x1, ref_y1 = x1, y1
                ref_x2, ref_y2 = x1, y1
            
            #Calculate max percentage diff
            diff = max_percentage_diff(
            x1,
            y1,
            x2,
            y2,
            ref_x1,
            ref_y1,
            ref_x2,
            ref_y2
            )
            
            #Assign output value to dict
            output_diffs[f][k].append(diff)
    
    #Assign input values to dict
    for k in params['var'].keys():
        output_diffs['input_params'][k].append(params['v1'][k])
    
    return output_diffs


def max_percentage_diff(x1, y1, x2, y2, ref_x1, ref_y1, ref_x2, ref_y2):
    """
    Return the max percentage diff.
    If there is a reference model,
    subtract its percentage diffs.
    """
    
    #Compute the minimum and maximum values of x
    xmin = max(min(x1),min(x2),min(ref_x1),min(ref_x2))
    xmax = min(max(x1),max(x2),max(ref_x1),max(ref_x2))
    
    #Interpolate linearly for all the data
    data1 = interpolate.interp1d(x1,y1)
    data2 = interpolate.interp1d(x2,y2)
    ref_data1 = interpolate.interp1d(ref_x1,ref_y1)
    ref_data2 = interpolate.interp1d(ref_x2,ref_y2)
    
    #Initialise max_diff to 0.
    max_diff = 0.
    #Calculate the relative difference
    therange = [x for x in x1 if xmin<=x<=xmax]
    for x in therange:
        #Try to avoid numerical divergences
        if data1(x) == 0. and data2(x) == 0.:
            diff = 0.
        else:
            diff = data2(x)/data1(x)-1.
        if ref_data1(x) == 0. and ref_data2(x) == 0.:
            ref_diff = 0.
        else:
            ref_diff = ref_data2(x)/ref_data1(x)-1.
        #Total diff
        tot_diff = 100.*np.fabs(diff-ref_diff)
        #Store max value
        if tot_diff > max_diff:
            max_diff = tot_diff
    
    return max_diff


def write_output_file(output_diffs, folders, args):
    """
    Write the output table.
    """
    
    array = []
    header = ''
    
    #Number of column
    count = 1
    #Columns with the input parameters
    for var in output_diffs['input_params'].keys():
        col = output_diffs['input_params'][var]
        array.append(col)
        header = header + str(count) + ':' + var + '    '
        count = count + 1
    
    #Columns with the output parameters
    for k in output_diffs.keys():
        if 'input_params' not in k:
            for var in output_diffs[k].keys():
                col = output_diffs[k][var]
                array.append(col)
                header = header + str(count) + ':' + k + ':' + var + '    '
                count = count + 1
    
    #Transpose array
    array = np.transpose(array)
    #File name
    fname = folders['main'] + folders['f_prefix'] + 'output.dat'
    #Save file
    np.savetxt(fname, array, header = header, delimiter='    ', fmt='%10.5e')
    
    return fname


def read_output_table(fname):
    """
    Read output file and return a dictionary
    with all the values.
    """
    
    #Initialise dictionary
    data_plots = {}
    
    try:
        with open(fname,'r') as f:
            header = f.readline()
            table = np.loadtxt(fname)
    except:
        raise IOError('--------> Output table not found!')
    
    #Divide headers
    header = header.strip('#')
    header = header.strip('\n')
    header = re.split('\d+:', header)
    header = [x.strip() for x in header]
    header = [x for x in header if x !='']
    
    #Transpose table
    table = np.transpose(table)
    
    #Generate dictionary
    for n in range(len(header)):
        prefix = header[n].split(':')[0]
        if prefix in gv.X_VARS.keys():
            data_plots[header[n]] = table[n]
    
    return data_plots


def generate_plots(data, folder):
    """
    Generate and save scatter plots for all the output data
    """
    
    for k in data.keys():
        x = range(1,len(data[k])+1)
        y = data[k]
        
        #File name
        fname = folder + re.sub(':', '_', k) + '.pdf'
        
        #x range
        delta_x = (max(x)-min(x))/40.
        x_min = min(x) - delta_x
        x_max = max(x) + delta_x
        plt.xlim(x_min,x_max)
        
        #Generate labels
        plt.xlabel('N')
        plt.ylabel('diff. [%]')
        plt.title(k)
        
        #Generate scatter plot
        plt.scatter(x, y, s=10)
        #Save plot
        plt.savefig(fname)
        #Close plot
        plt.close()
    
    return