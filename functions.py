def read_ini_file(input_file):
    """ Open and read the input file

    Args:
        input_file: path to the input_file.

    Returns:
        dictionary with all the parameters of the input_file.

    """
    
    params = {}
    with open(input_file, "r") as f:
        for line in f:
            if "=" in line:
                line = line.replace(" ", "")
                line = line.rstrip()
                (key, val) = line.split("=")
                
                #If val is a string that contains ",", try to convert it in a range of numbers
                #otherwise leave it as it is
                #If val is a range of numbers choose randomly a number in that interval
                if "," in val:
                    args = val.split(",")
                    if len(args) == 2:
                        try:
                            x_min = float(args[0])
                            x_max = float(args[1])
                            
                            import random
                            val = random.uniform(x_min, x_max)
                        except:
                            pass
                
                #For each line assign the value obtained to the key
                params[key] = val
    
    
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



def create_ini_file(input_file, init_dir, output_dir):
    """ Generates and write the init_file for each model from the input file

    Args:
        input_file: path to the input_file.
        init_dir: folder where to store the init_file.
        output_dir: folder where to store the output of the init_file.

    Returns:
        path of the init_file.

    """
    
    #Open and read the input_file
    f= read_ini_file(input_file)
    
    
    
    return input_file