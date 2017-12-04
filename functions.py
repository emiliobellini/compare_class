#This module contains all the functions needed by the compare.py module.
import os
import re
import sys
import argparse
import random
import subprocess
import fnmatch
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
    info_parser = subparsers.add_parser('info')
    
    #Arguments for 'run'
    run_parser.add_argument('input_file', type=str, help='Input file')
    run_parser.add_argument('--params-v1', type=str, default = None,
    help='Input file only for class-v1')
    run_parser.add_argument('--params-v2', type=str, default = None,
    help='Input file only for class-v2')
    run_parser.add_argument('-N', type=int, default=1,
    help='Number of iterations (default = 1)')
    run_parser.add_argument('--want-plots', action='store_true',
    help='Generate plots from the output')

    #Arguments for 'info'
    info_parser.add_argument('--output-dir', '-o', type=str,
    default = None, help='Folder where the output table is stored')

    args = parser.parse_args()
    
    return args


def read_input_parameters(args):
    """
    Read the input parameters.
    
    Return a dict with the parameters (keys: 'common', 'v1', 'v2').
    """
    
    #Define the main dictionary params
    params = {}
    
    #Define three different dictionaries for parameters
    params['common'] = {}
    params['v1'] = {}
    params['v2'] = {}
    
    #Read the common parameters
    params['common'] = read_ini_file(args.input_file)
    
    #Read parameters for class_v1
    if args.params_v1 is not None:
        params['v1'] = read_ini_file(args.params_v1)
    
    #Read parameters for class_v2
    if args.params_v2 is not None:
        params['v2'] = read_ini_file(args.params_v2)
    
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
                (key, val) = line.split("=")
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
    fname = params['common']['root_class_v2']
    folders['v2'] = folder_exists_or(fname, 'error')

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
    
    #Assign to params of each version of class the relative path of
    #the tmp folder, which will be used by class to store the outputs
    fname = os.path.relpath(folders['tmp']) + '/' + folders['f_prefix']
    params['v1']['root'] = fname + 'v1_'
    params['v2']['root'] = fname + 'v2_'

    #Remove roots from params
    params.pop('f_prefix', None)
    params.pop('root', None)
    params['common'].pop('root_class_v1', None)
    params['common'].pop('root_class_v2', None)
   
    return params, folders


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
        if "__1" in key:
            new_keys.append(key.strip("__1"))

    for new_key in new_keys:
        count=0
        new_val = ''
        for key in params.keys():
            if new_key in key:
                count += 1
        for i in range(count):
            old_key = new_key + '__' + str(i+1)
            new_val += str(params[old_key]) + ','
            params.pop(old_key, None)
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
    #Get the path to the ini file
    ini_path = folders['main'] + folders['f_prefix'] + v + '.ini'
    #Run class
    subprocess.call([class_path, ini_path])
    
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

# def find_common_output(v1, v2, files_to_compare, dir_files):
#     """ Find the common files in the output folder
# 
#     Args:
#         v1: dictionary containing properties of the first version of class.
#         v2: dictionary containing properties of the second version of class.
#         files_to_compare: name of the files to compare.
#         dir_files: files in the output folder.
# 
#     Returns:
#         List of common files.
# 
#     """
# 
#     common_output = []
#     seen = set()
#     for co in dir_files:
#         co = co.split('.')[0]
#         co = co.replace(v1['ini_name'] + '_', '')
#         co = co.replace(v2['ini_name'] + '_', '')
#         if co in files_to_compare:
#             if co not in seen:
#                 common_output.append(co)
#                 seen.add(co)
# 
#     return common_output
# 
# 
# 
# def import_output(v, common_output, output_dir):
#     """ Find the common files in the output folder
# 
#     Args:
#         v: dictionary containing properties of each version of class.
#         common_output: suffix of the files to compare.
#         output_dir: path of the output folder.
# 
#     Returns:
#         Dictionary with all the output of each file.
# 
#     """
# 
#     import numpy as np
#     import re
# 
#     for co in common_output:
#         v['output'][co] = {}
# 
#         #Set the name and the path of the file
#         output_file = output_dir + v['ini_name'] + '_' + co + '.dat'
#         #Open the file and read the values
#         content = np.genfromtxt(output_file)
#         #Transpose table
#         content = content.transpose()
#         #Open the file and read the header
#         with open(output_file, 'r') as f:
#             #Read each line
#             headers = f.read().splitlines()
#             #Select only lines that start with #
#             headers = [x for x in headers if x[0] == '#']
#             #Select only the last line with # (it is the line containing the headers)
#             headers = headers[-1]
#             #Manipulate headers to get something readable
#             headers = re.sub('#','',headers)
#             headers = headers.split('  ')
#             headers = [x for x in headers if x !='']
#             headers = [x for x in headers if x !=' ']
#             headers = [x.strip(' ') for x in headers]
#             headers = [x.split(':')[-1] for x in headers]
# 
#         #Create dictionary with the variables associated to their values
#         for i in range(len(headers)):
#             v['output'][co][headers[i]] = content[i]
# 
# 
#     return
# 
# 
# 
# def return_max_percentage_diff(x1, y1, x2, y2):
#     """ Return the max percentage difference for each variable of a file
# 
#     Args:
#         x1: array containing the values of the independend variable of class_v1.
#         y1: array containing the values of the dependend variable of class_v1.
#         x2: array containing the values of the independend variable of class_v2.
#         y2: array containing the values of the dependend variable of class_v2.
# 
#     Returns:
#         The maximum percentage difference between the two outputs.
# 
#     """
# 
#     import numpy as np
#     from scipy import interpolate
# 
#     #Compute the minimum and maximum values of x
#     xmin = max(min(x1),min(x2))
#     xmax = min(max(x1),max(x2))
# 
#     #Interpolate linearly for [x1, y1] and [x2, y2]. Then we will calculate
#     #the diffs w.r.t. the points of [x1, y1]
#     data1 = interpolate.interp1d(x1,y1)
#     data2 = interpolate.interp1d(x2,y2)
# 
#     #Initialise max_diff to 0.
#     max_diff = 0.
#     #Calculate the relative difference
#     therange = [x for x in x1 if xmin<=x<=xmax]
#     for x in therange:
#         if data1(x) == 0. and data2(x) == 0.:
#             diff = 0.
#         else:
#             diff = np.fabs(data2(x)/data1(x)-1.)
#         if diff > max_diff:
#             max_diff = diff
# 
#     return 100*max_diff
# 
# 
# 
# def generate_plots(data, output_dir):
#     """ Generate and save scatter plots for all the output data
# 
#     Args:
#         data: dictionary with all the output data.
#         output_dir: folder where to save the plots.
# 
#     Returns:
#         Scatter plots for the output data.
# 
#     """
# 
#     import numpy as np
#     import matplotlib.pyplot as plt
#     import re
# 
#     for k in data.keys():
#         x = [x+1 for x in range(len(data[k]))]
#         y = data[k]
# 
#         #Name for the output
#         new_k = re.sub('\s.+', '', k)
#         new_k = re.sub(':', '_', new_k)
#         file_name = output_dir + '_' + new_k + '.pdf'
# 
#         #Decide x range
#         delta_x = (max(x)-min(x))/40.
#         x_min = min(x) - delta_x
#         x_max = max(x) + delta_x
#         plt.xlim(x_min,x_max)
#         #Generate labels
#         plt.ylabel('N')
#         plt.ylabel('diff. [%]')
#         plt.title(k)
# 
#         #Generate scatter plot
#         plt.scatter(x, y, s=10)
# 
#         #Save plot
#         plt.savefig(file_name)
# 
#         #Close plot
#         plt.close()
# 
#     return
