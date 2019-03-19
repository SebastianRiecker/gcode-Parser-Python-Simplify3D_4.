# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas.plotting import scatter_matrix

'''
Purpose:
Gcode parser was coded to read Simplify3D (V4.0) printing setups that are nested in the gcode file (comment at the beginning)
and convert them into a csv file for exportation into excel or further usage for analysis (pandas).
'''
def get_gcode_paths_names():
    '''Asks for inputpath, returns lists: filepath, gcode_name '''
    import glob
    import os
    inputpath  = input('Ordnerpfad der Gcodes?:')
    os.chdir(inputpath)
    filepath   = glob.glob('./*.gcode')
    filepath   = sorted(filepath)
    filename   = list(map(os.path.basename, filepath))
    name       = [x.split('.')[0] for x in filename]
    return filepath, filename, name

def get_protocoll_paths_names():
    '''Asks for inputpath, returns lists: filepath, protocoll_name '''
    import glob,os.path
    inputpath  = input('Ordnerpfad des Protokolls (F3P.csv)?:')
    os.chdir(inputpath)
    filepath   = glob.glob('./*F3P.csv')
    filepath   = sorted(filepath)
    filename = list(map(os.path.basename, filepath))
    name       = [x.split('.')[0] for x in filename]
    return filepath, filename, name

def read_gcode(filepath):
    '''reads out gcode settings - for Simplify3D, V4.0'''
    import pandas as pd
    gcode_df = pd.read_csv(filepath, sep=',', skiprows=3, nrows=192, names=list('xabcd'), comment = '|', skipinitialspace=True )
    gcode_df = gcode_df.replace({';   ': ''}, regex=True)
    gcode_df = gcode_df.set_index('x')
    return gcode_df

def read_protocoll(filepath):
    '''reads out FFF protocoll'''
    import pandas as pd
    protocoll_df = pd.read_csv(filepath, sep=';', skiprows=1, skipinitialspace=True )
    protocoll_df = protocoll_df.set_index('Druckjob')
    #protocoll_df = protocoll_df.set_index('')
    return protocoll_df

def clean_gcodesnippets(df):
    '''cleans out gcode snippets from dataframe'''
    import pandas as pd
    gcode_df = df.drop(['startingGcode','layerChangeGcode', 'retractionGcode', 'toolChangeGcode', 'endingGcode', 'firmwareTypeOverride'])
    return gcode_df

def choose_main_nozzle(df):
    '''select main nozzle based on chosen setup profile in Simplify3D V4.0 gcode'''
    import pandas as pd
    if df.loc['primaryExtruder'][0]==0:
        main_extruder_column = 'a'
    if df.loc['primaryExtruder'][0]==1:
        main_extruder_column = 'b'
    else:
        main_extruder_column = 'a'
    return main_extruder_column

def append_date(filepath, df4col):
    '''read out date in Simplify3D V4.0 gcode '''
    import pandas as pd
    datetime  = pd.read_csv(filepath, sep=';', header = None, skiprows=1, nrows=1)
    date_df   = pd.DataFrame({'a': datetime[1][0], 'b': 'NaN', 'c': 'NaN', 'd': 'NaN'}, index = ['date']) # ERROR
    gcode_df  = pd.concat([date_df, df4col], axis=0)
    return gcode_df

def append_temp(df):
    '''read out chamber and bed temp + sort it behind nozzle temp'''
    import pandas as pd
    temperatureChamber = df.loc['temperatureSetpointTemperatures','d']
    temperatureBed     = df.loc['temperatureSetpointTemperatures','c']
    df_T   = pd.DataFrame({'a': [temperatureBed,temperatureChamber]}, index = ['temperatureSetpointTemperaturesBed','temperatureSetpointTemperaturesChamber'])
    df_out = pd.concat([df,df_T])
    return df_out

def reduce_to_main_nozzle(df):
    ''' reduces gcode columns (4) to only first column, copy main nozzle in first column first'''
    import pandas as pd
    main_noz = choose_main_nozzle(df)
    if main_noz == 'b':
        df.loc['extruderName':'extruderWipeDistance','a'] = df.loc['extruderName':'extruderWipeDistance', 'b']
        df.loc['temperatureName':'temperatureRelayBetweenLoops', 'a'] = df.loc['temperatureName':'temperatureRelayBetweenLoops', 'b']
    df = df['a']
    return df

def start_gcode_df_blanc(filepath, namelist):
    '''Get List of gcode data and generate empty (0) DataFrame with indices on top out of FIRST gcode'''
    import pandas as pd
    gcode_df     = read_gcode(filepath[0])
    #gcode_df     = clean_gcodesnippets(gcode_df)
    gcode_df     = append_temp(gcode_df)
    date_df      = pd.DataFrame(data=None, index= namelist ,columns=['date']) #create blanc Dataframe with index date
    gcode_df_all = pd.DataFrame(data=np.zeros((len(namelist),len(gcode_df.index.values))), index=namelist, columns=gcode_df.index.values, dtype=None, copy=False)
    gcode_df_all = pd.concat([date_df, gcode_df_all], axis=1)
    return gcode_df_all

def insert_gcode_df_data(filepath, df, i):
    '''Get gcode data and export values as array'''
    import pandas as pd
    gcode_df        = read_gcode(filepath[i])
    #gcode_df        = clean_gcodesnippets(gcode_df)
    gcode_df        = append_temp(gcode_df)
    gcode_df        = append_date(filepath[i], gcode_df)
    gcode_df        = reduce_to_main_nozzle(gcode_df)
    df.iloc[i]      = gcode_df.values
    return df

def clean_columns(DF):
    '''drop columns that are all NAN'''
    DFclean = DF.dropna(axis=1, how='all') 
    return DFclean
    
def clean_rows(DF):
    ''' drop rowas that contain NAN'''
    DFclean = DF.dropna(axis=0, how='any')
    return DFclean

###################
### run program ###
###################
# Gcode      = gc
# Protocoll  = pc

# read Gcode in DataFrame (gc_df)
gc_filepath,gc_filename,gc_name = get_gcode_paths_names()
gc_df                           = start_gcode_df_blanc(gc_filepath, gc_name) # filepath/folderpath? # ERROR date_df append
for i in np.arange(len(gc_filepath)):
    insert_gcode_df_data(gc_filepath, gc_df, i)

# read protocoll in DataFrame (pc_df)
pc_filepath,pc_filename,pc_name = get_protocoll_paths_names()
pc_df = read_protocoll(pc_filepath[0])

# Concat Dataframes for protocoll
DF = pd.concat([pc_df, gc_df], axis=1)

## Output

#1 Gcode-DataFrame full Setup (containing NaN)
gc_df.to_csv('Gcode_DataFrame.csv', sep=';', decimal=',', header=True)
print ('CHECK - Output Gcode_DataFrame.csv')

#2 Gcode-DataFrame rows synchronized with protocoll data
DF.loc[:,'date':].to_csv('Gcode_DataFrame_synced.csv', sep=';', decimal=',', header=True)
print ('CHECK - Output Gcode_DataFrame_synced.csv')

