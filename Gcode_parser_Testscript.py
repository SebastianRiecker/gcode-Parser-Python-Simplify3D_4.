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
transfer_rows = gpm.get_transfer_rows(gc_sort)
transfer_rows.plot(y = 'length', kind='hist', logy=True)
transfer_rows.plot(y = 'duration', kind='hist', logy=True)
transfer_rows.plot(x='layer', y='length', kind='scatter')

#dataframe = gc
#gcx = gc.iloc[60:80]
#ar = data_array[20:80]







# =============================================================================
# # OPTIMIZATION
# =============================================================================

    # look at first 5 elements of row in dataframe: [1:5] - thats where the parameters are
for rownumber in np.arange(len(data_array)): 
    rel_range = [1,2,3,4,5]
    for i in rel_range:  # all columns except command
        input_cell = dataframe.iloc[rownumber, i]
        if input_cell != '0':
            command_val = float(input_cell[1:])
            command_char = input_cell[0]
            array_position = column_names.index(command_char)
            data_array[rownumber, array_position] = command_val
 
           
        picked_cell = dataframe.iloc[rownumber,1:5][dataframe.iloc[rownumber,1:5].str.contains(column_names[i])]
        if not picked_cell.empty:
            data_array[rownumber, i] = get_command_parametervalue(picked_cell[0])  # [0] to get value, not series-element
    






# =============================================================================
# # TIMEIT
# =============================================================================

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
    
dataframe = import_gcode(path, column_names)

relevant = ['X', 'Y', 'Z', 'E', 'F', 'S']  # contain gcode-values
rel_index = [column_names.index(s) for s in column_names for x in relevant if x == s]
data_array = np.zeros([len(dataframe), len(column_names)]) # without command column (-1)

'''

test = '''\
for rownumber in np.arange(len(data_array)): 
    rel_range = [1,2,3,4,5]  # relevant lookup positions in dataframe
    for i in rel_range:  # all columns except command
        input_cell = dataframe.iloc[rownumber, i]
        if input_cell != '0':
            try:
                data_array[rownumber, column_names.index(input_cell[0])] = float(input_cell[1:])
            except ValueError:
                pass  # if not in clumn_names, then no assignment necessary
'''

t = timeit.timeit(stmt = test, setup = setupx, number = 1)
print(t)


setupx = '''\
import numpy as np
a = np.arange(100).reshape(10,10)
'''

test = '''\


x = a[(2*3),(2*4)]
'''

test = '''\
p1 = 2*3
p2 = 2*4
x = a[p1,p2]
'''

t = timeit.timeit(stmt = test, setup = setupx, number = 1000000)
print(t)

