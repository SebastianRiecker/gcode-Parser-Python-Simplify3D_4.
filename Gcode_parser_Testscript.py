# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:13:55 2019

@author: Sebastian
"""

import os
os.chdir('C:\\Users\\Sebastian\\Documents\\gcode-Parser-Python-Simplify3D_4')
import Gcode_parser_module as gpm

# FIX INITISLIZATION
column_names = ['command', 'command_group', 'layer', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'transfer', 'length', 'duration']
path = 'D:\_Business\Arbeit\Fraunhofer IFAM_DD\Python\FFF gcode parser\_gcode\TEST.gcode'

# DATA IMPORT AND PARSING
gc = gpm.import_gcode(path, column_names)
gc_sort = gpm.generate_sorted_dataframe(gc, column_names)

# DATA ANALYSIS
print('Print time: %0.2f min' %gc_sort['duration'].sum())
transfer_stats = gpm.get_transfer_stats(gc_sort)
transfer_stats.hist(column = 'length')
transfer_stats.hist(column = 'duration')


#dataframe = gc
#gcx = gc.iloc[60:80]
#ar = data_array[20:80]


# TIMEIT

import timeit

setupx = '''\
import numpy as np
import pandas as pd
import io
column_names = ['command', 'command_group', 'layer', 'X', 'Y', 'Z', 'E', 'F', 'S', 'P', 'H', 'transfer', 'length', 'duration']
path = 'D:\\_Business\\Arbeit\\Fraunhofer IFAM_DD\\Python\\FFF gcode parser\\_gcode\\TEST.gcode'

def import_gcode(filepath, column_names):
    import pandas as pd
    gcode_df = pd.read_csv(filepath, sep = ' ', 
                           comment = ';',
                           names = column_names)
    gcode_df = gcode_df.fillna('0')
    return gcode_df

def get_command_parametervalue(parameter_str):
    GM = ['G', 'M']  # check that is not command but parameter
    if any(x in parameter_str for x in GM):
        command_value = parameter_str
    else:
        command_value = float(parameter_str[1:])
    return command_value
    
dataframe = import_gcode(path, column_names)

relevant = ['X', 'Y', 'Z', 'E', 'F', 'S']  # contain gcode-values
rel_index = [column_names.index(s) for s in column_names for x in relevant if x == s]
data_array = np.zeros([len(dataframe), len(column_names)]) # without command column (-1)

'''

test = '''\
for rownumber in np.arange(len(data_array)): 
    for i in rel_index:  # all columns except command
        picked_cell = dataframe.iloc[rownumber,1:5][dataframe.iloc[rownumber,1:5].str.contains(column_names[i])]
        #if not picked_cell.empty:
            #data_array[rownumber, i] = get_command_parametervalue(picked_cell[0])  # [0] to get value, not series-element
'''

t = timeit.timeit(stmt = test, setup = setupx, number = 1)
print(t)