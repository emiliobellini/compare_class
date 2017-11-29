def read_ini_file(input_file):
    """ Open and read the input file

    Args:
        input_file: path to the input_file.

    Returns:
        dictionaries with all the parameters of the input_file:
            fix_params: for the fixed parameters
            var_params: for the varied parameters

    """
    
    import re
    
    fix_params = {}
    var_params = {}
    with open(input_file, "r") as f:
        for line in f:
            if "=" in line and line[0] != '#':
                line = re.sub('#.+', '', line)
                (key, val) = line.split("=")
                key = key.strip()
                val = val.strip()
                
                #If a key contains a val with two floats separated by comma,
                #it considers it as a varying parameter, otherwise fixed.
                if "," in val and len(val.split(",")) == 2:
                    try:
                        float(val.split(",")[0])
                        float(val.split(",")[1])
                        
                        #Assign to var_params the key
                        var_params[key] = val
                    except:
                        #Assign to fix_params the key
                        fix_params[key] = val
                else:
                    #Assign to fix_params the key
                    fix_params[key] = val


    return fix_params, var_params



def generate_random(params):
    """ Generate random values from ranges

    Args:
        params: dictionary with varying parameters.

    Returns:
        new_params: new dictionary with random numbers instead of ranges
    """
    
    new_params = {}
    for k in params.keys():
        val = params[k]
        val = val.split(",")
        try:
            #Try to generate a random number in the range
            x_min = float(val[0].strip())
            x_max = float(val[1].strip())
            import random
            new_params[k] = random.uniform(x_min, x_max)
        except:
            raise
    
    return new_params



def group_parameters(params_1, params_2):
    """ Group together parameters

    Args:
        params_1: dictionary parameters.
        params_2: dictionary parameters.

    Returns:
        params: a single dictionary with the parameters grouped together
    """
    
    #Merge the two dictionaries
    params = params_1.copy()
    params.update(params_2)
    
    #Group together keys that refer to the same parameter in (hi_)class
    #e.g. (parameters_smg__1 with parameters_smg__2)
    new_keys = []
    for key in params.keys():
        if "__1" in key:
            new_keys.append(key.strip("__1"))
    
    for new_key in new_keys:
        new_val = ''
        count=0
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



def create_ini_file(v, params, output_dir):
    """ Write the parameter file

    Args:
        v: dictionary containing properties of each version of class.
        params: dictionary of the common parameters.
        output_dir: relative path to the folder where to store the ini file and the outputs.

    Returns:
        The folder containing the output parameters.

    """
    
    #Merge the two dictionaries
    params = params.copy()
    params.update(v['params'])
    
    #Add root for the output (it is the relative path w.r.t. base_dir)
    output_name = v['ini_path'].split('/')[-1]
    output_name = output_name.split('.')[0]
    params['root'] = output_dir + output_name + '_'
    
    
    #Create the file
    with open(v['ini_path'], 'w') as f:
        for k in params.keys():
            f.write(str(k) + ' = ' + str(params[k]) + '\n')
    
    return params['root']



def run_class(v):
    """ Run the current version of class

    Args:
        v: dictionary containing properties of each version of class.

    Returns:
        None.

    """
    import subprocess
    
    subprocess.call([v['root'] + 'class', v['ini_path']])
    
    return



def find_common_output(v1, v2, files_to_compare, dir_files):
    """ Find the common files in the output folder

    Args:
        v1: dictionary containing properties of the first version of class.
        v2: dictionary containing properties of the second version of class.
        files_to_compare: name of the files to compare.
        dir_files: files in the output folder.

    Returns:
        List of common files.

    """
    
    common_output = []
    seen = set()
    for co in dir_files:
        co = co.split('.')[0]
        co = co.replace(v1['ini_name'] + '_', '')
        co = co.replace(v2['ini_name'] + '_', '')
        if co in files_to_compare:
            if co not in seen:
                common_output.append(co)
                seen.add(co)
    
    return common_output



def import_output(v, common_output, output_dir):
    """ Find the common files in the output folder

    Args:
        v: dictionary containing properties of each version of class.
        common_output: suffix of the files to compare.
        output_dir: path of the output folder.

    Returns:
        Dictionary with all the output of each file.

    """
    
    import numpy as np
    
    for co in common_output:
        v['output'][co] = {}
        
        #Set the name and the path of the file
        output_file = output_dir + v['ini_name'] + '_' + co + '.dat'
        #Open the file and read the values
        content = np.genfromtxt(output_file)
        #Transpose table
        content = content.transpose()
        #Open the file and read the header
        with open(output_file, 'r') as f:
            #Read each line
            headers = f.read().splitlines()
            #Select only lines that start with #
            headers = [x for x in headers if x[0] == '#']
            #Select only the last line with # (it is the line containing the headers)
            headers = headers[-1][1:]
            #Manipulate headers to get something readable
            headers = headers[1:].split('  ')
            headers = [x for x in headers if x !='']
            headers = [x for x in headers if x !=' ']
            headers = [x.strip(' ') for x in headers]
            headers = [x.split(':')[-1] for x in headers]
            
        #Create dictionary with the variables associated to their values
        for i in range(len(headers)):
            v['output'][co][headers[i]] = content[i]
        

    return



def return_max_percentage_diff(x1, y1, x2, y2):
    """ Return the max percentage difference for each variable of a file

    Args:
        x1: array containing the values of the independend variable of class_v1.
        y1: array containing the values of the dependend variable of class_v1.
        x2: array containing the values of the independend variable of class_v2.
        y2: array containing the values of the dependend variable of class_v2.

    Returns:
        The maximum percentage difference between the two outputs.

    """
    
    import numpy as np
    from scipy import interpolate
    
    #Compute the minimum and maximum values of x
    xmin = max(min(x1),min(x2))
    xmax = min(max(x1),max(x2))
    
    #Interpolate linearly for [x1, y1] and [x2, y2]. Then we will calculate
    #the diffs w.r.t. the points of [x1, y1]
    data1 = interpolate.interp1d(x1,y1)
    data2 = interpolate.interp1d(x2,y2)
    
    #Initialise max_diff to 0.
    max_diff = 0.
    #Calculate the relative difference
    therange = [x for x in x1 if xmin<=x<=xmax]
    for x in therange:
        if data1(x) == 0. and data2(x) == 0.:
            diff = 0.
        else:
            diff = np.fabs(data2(x)/data1(x)-1.)
        if diff > max_diff:
            max_diff = diff
    
    return 100*max_diff



def generate_plots(data, output_dir):
    """ Generate and save scatter plots for all the output data

    Args:
        data: dictionary with all the output data.
        output_dir: folder where to save the plots.

    Returns:
        Scatter plots for the output data.

    """
    
    import numpy as np
    import matplotlib.pyplot as plt
    import re
    
    for k in data.keys():
        x = [x+1 for x in range(len(data[k]))]
        y = data[k]
        
        #Name for the output
        new_k = re.sub('\s.+', '', k)
        new_k = re.sub(':', '_', new_k)
        file_name = output_dir + '_' + new_k + '.pdf'
        
        #Decide x range
        delta_x = (max(x)-min(x))/40.
        x_min = min(x) - delta_x
        x_max = max(x) + delta_x
        plt.xlim(x_min,x_max)
        #Generate labels
        plt.ylabel('N')
        plt.ylabel('diff. [%]')
        plt.title(k)
        
        #Generate scatter plot
        plt.scatter(x, y)
        
        #Save plot
        plt.savefig(file_name)
    
    return
