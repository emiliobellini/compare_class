#This module contains all the constants that the user may want to change,
#and that are passed through the different modules.

#Independent variables for each file
X_VARS = {
    'background': 'z',
    'cl': 'l',
    'pk': 'k'
}

#Dependent variables for each file
Y_VARS = {
    'background': ['H'],
    'cl': ['TT', 'EE'],
    'pk': ['P']
}

#Dictionary between names of variables as written in the class output,
#and names given internally in this code
DICTIONARY = {
    'background': {'H [1/Mpc]' : 'H'},
    'pk': {'k (h/Mpc)' : 'k',
           'P (Mpc/h)^3' : 'P'
          }
}
