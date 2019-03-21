# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 20:44:10 2019

@author: Sebastian
"""

column_names = ['command', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'dX', 'dY', 'dZ', 'dE', 'transfer', 'line_length', 'duration']

def import_gcode(filepath):
    '''reads out gcode settings out of comments in first lines - for Simplify3D, V4.0.
    Due to bad protocoll form, lots of columns needed for the case, that several temperature setpoints
    are given.'''
    import pandas as pd
    gcode_df = pd.read_csv(filepath, sep = ' ', 
                           comment = ';',
                           names = ['command', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'dX', 'dY', 'dZ', 'dE', 'transfer', 'line_length', 'duration'])  
    gcode_df = gcode_df.fillna('0')
    return gcode_df


def get_command_parametervalue(parameter_str):
    '''Separates and returns command parameter values from letter (e.g. X3.45 --> 3.45), if not command itself (M or G)'''
    GM = ['G', 'M']  # check that is not command but parameter
    if any(x in parameter_str for x in GM):
        command_value = parameter_str
    else:
        command_value = float(parameter_str[1:])
    return command_value


def generate_sorted_dataframe(dataframe, column_names):
    ''' Function does the following:
        Generate new DataFrame with columns according to column names
        Import numeric data into np.array with same length and one less column (faster)
            > look at each element of column_names and search in row for a str-match
            > take the value of the matched command parameter and write into array
        Transfer to new dataframe'''
    import numpy as np
    import pandas as pd
    relevant = ['X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H']  # contain gcode-values
    rel_index = [column_names.index(s) for s in column_names for x in relevant if x == s]
    data_array = np.zeros([len(dataframe), len(column_names[1:])]) # without command column (-1)
    
    for rownumber in np.arange(len(data_array)): 
        for i in rel_index:  # all columns except command
            picked_cell = dataframe.iloc[rownumber][dataframe.iloc[rownumber].str.contains(column_names[i])]
            if not picked_cell.empty:
                data_array[rownumber, i-1] = get_command_parametervalue(picked_cell[0])  # [0] to get value, not series-element
            
    array_df = pd.DataFrame(data_array,columns = column_names[1:])
    new_dataframe = pd.concat([dataframe.iloc[:,0],array_df], axis=1)
    return new_dataframe
        