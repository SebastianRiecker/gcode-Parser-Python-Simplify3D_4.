# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 20:44:10 2019

@author: Sebastian
"""

# SET names!
# 'command', ' command_group', 'layer', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'transfer', 'length', 'duration'
column_names = ['command', 'command_group', 'layer', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'transfer', 'length', 'duration']

def import_gcode(filepath, column_names):
    '''reads out gcode settings out of comments in first lines - for Simplify3D, V4.0.
    Due to bad protocoll form, lots of columns needed for the case, that several temperature setpoints
    are given.'''
    import pandas as pd
    gcode_df = pd.read_csv(filepath, sep = ' ', 
                           comment = ';',
                           names = column_names)
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
    relevant = ['X', 'Y', 'Z', 'E', 'F', 'S']  # contain gcode-values
    rel_index = [column_names.index(s) for s in column_names for x in relevant if x == s]
    data_array = np.zeros([len(dataframe), len(column_names)]) # without command column (-1)
    
    # look at first 5 elements of row in dataframe: [1:5] - thats where the parameters are
    for rownumber in np.arange(len(data_array)): 
        for i in rel_index:  # all columns except command
            picked_cell = dataframe.iloc[rownumber,1:5][dataframe.iloc[rownumber,1:5].str.contains(column_names[i])]
            if not picked_cell.empty:
                data_array[rownumber, i] = get_command_parametervalue(picked_cell[0])  # [0] to get value, not series-element
    

    add_set_parametervalues(data_array, column_names.index('F')) 
    add_set_parametervalues(data_array, column_names.index('Z'))
    assign_layer_number(data_array, column_names.index('Z'), column_names.index('layer'))
    assign_length(data_array, column_names.index('X'), column_names.index('Y'), column_names.index('Z'), column_names.index('length'))
    assign_duration(data_array, column_names.index('length'), column_names.index('F'), column_names.index('duration'))
    assign_command_group(data_array, dataframe, column_names.index('command_group'))
    
    array_df = pd.DataFrame(data_array[:,1:], columns = column_names[1:])
    new_dataframe = pd.concat([dataframe.loc[:, 'command'],array_df], axis=1)
    return new_dataframe


def assign_length(array, col_X, col_Y, col_Z, col_write):
    '''Calculate length of movement based on XYZ-coordinates of current and last position. Assign to col_write.'''
    import numpy as np
    last_x = 0
    last_y = 0
    for row in array:
        if row[col_X] and row[col_Y]:
            dx = abs(row[col_X]-last_x)
            dy = abs(row[col_Y]-last_y)
            row[col_write] = np.sqrt(dx**2 + dy**2)
            last_x = row[col_X] 
            last_y = row[col_Y]


def assign_duration(array, col_length, col_F, col_write):
    '''Calculate duration of movement from length and speed (F, [F] = mm/min) and assign to col_write.'''
    for row in array:
        if row[col_F] != 0:
            row[col_write] = row[col_length]/row[col_F]
        
def add_set_parametervalues(array, col_number):
    '''Fill in the parameter values that are already set, but do not change in current line and therefore are 0.'''
    last_val = 0
    for row in array:
        if row[col_number] == 0:
            row[col_number] = last_val
        last_val = row[col_number]


def assign_command_group(array, dataframe, col_write):
    '''Group the commands if the same command is repeated (e.g. 100xG1 for 100 lines) and assign command_group value
    to row. This way, the duration of more complex travel movements can be calculated.'''
    command_group = 0
    last_command = dataframe.loc[0, 'command']
        
    for i, row in enumerate(array):
        command = dataframe.loc[i,'command']
        if command != last_command:
            command_group += 1
        row[col_write] = command_group
        last_command = dataframe.loc[i, 'command']

     
def assign_layer_number(array, col_z, col_write):
    '''Look at current z-height and assign layer number to col_write. '''
    last_z = 0
    layer_number = 0
    for row in array:
        if row[col_z] > last_z:
            layer_number += 1
        row[col_write] = layer_number
        last_z = row[col_z]      
        
        
def get_transfer_stats(dataframe):
    G1_rows = dataframe[dataframe.loc[:,'command'] == 'G1']
    transfer_rows = G1_rows[G1_rows.loc[:,'E'] == 0]
    
    df_result_sum = transfer_rows.groupby(['command_group']).sum()
    return df_result_sum
