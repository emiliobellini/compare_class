def read_ini_file(input_file):
    """ Open and read the input file

    Args:
        input_file: path to the input_file.

    Returns:
        dictionaries with all the parameters of the input_file:
            fix_params: for the fixed parameters
            var_params: for the varied parameters

    """
    
    fix_params = {}
    var_params = {}
    with open(input_file, "r") as f:
        for line in f:
            if "=" in line:
                line = line.replace(" ", "")
                line = line.rstrip()
                (key, val) = line.split("=")
                
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
            x_min = float(val[0])
            x_max = float(val[1])
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
        new_ini: path to the new ini file.
        params_1: first dictionary of parameters.
        params_2: second optional dictionary of parameters.
        output_dir: relative path to the folder where to store the ini file and the outputs.
        base_dir: folder containing this script.

    Returns:
        path of the init_file.

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
    
    return 