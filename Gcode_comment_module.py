# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

'''
Purpose:
Gcode parser was coded to read Simplify3D (V4.0) printing setups that are nested in the gcode file (comment at the beginning)
and convert them into a csv file for exportation into excel or further usage for analysis (pandas).
'''
def get_gcode_path_names():
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


def import_gcode_printparameters(filepath):
    '''reads out gcode settings out of comments in first lines - for Simplify3D, V4.0.
    Due to bad protocoll form, lots of columns needed for the case, that several temperature setpoints
    are given.'''
    import pandas as pd
    gcode_df = pd.read_csv(filepath, sep = ',', 
                           skiprows = 3, 
                           nrows = 192, 
                           names = ['index', 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], # for temp settings 
                           warn_bad_lines = True,  # if not all columns are read in
                           skipinitialspace = True )  # skip space after delimiter

    gcode_df = gcode_df.dropna(axis=1, how='all')
    gcode_df = gcode_df.replace({';   ': ''}, regex = True)  # cut off left spaces
    gcode_df = gcode_df.set_index('index')
    return gcode_df

def import_gcode_stats(filepath):
    '''Reads out gcode stats given at the end of the gcode as comment (Simplify3D)'''
    import pandas as pd
    with open(filepath) as f:
        row_number = sum(1 for line in f)  # count number of lines in gcode
    build_stats = pd.read_csv(filepath, sep = ':', 
                           skiprows = row_number-5,  # read only last 5 lines 
                           nrows = 192, 
                           names = ['index', 'value'], # for temp settings 
                           warn_bad_lines = True,  # if not all columns are read in
                           skipinitialspace = True )  # skip space after delimiter
    build_stats = build_stats.replace({';   ': ''}, regex = True)
    build_stats = build_stats.set_index('index')
    return build_stats

def delete_rows_with_gcodescripts(dataframe):
    '''Find rows where index contains the string Gcode and drop them'''
    dataframe_new = dataframe.drop(index = dataframe.index[dataframe.index.str.contains('Gcode')])
    return dataframe_new

# =============================================================================
# TODO
# =============================================================================
def rearrange_temperature_data(dataframe):
    '''Find rows containing temperature data. make new row for each left right, bed or chamber params.
    '''
    dataframe_temperature = gcode.index[gcode.index.str.contains('temperature')]
    
    return dataframe_new


def import_protocol(filepath, sheet_name='V2'):
    '''read excel sheet "sheet_name" and return as pandas dataframe'''
    import pandas as pd
    protocoll_dataframe = pd.read_excel(filepath, 
                                        sheet_name=sheet_name, 
                                        header=1, 
                                        index_col=1, 
                                        usecols='A:AU')
    return protocoll_dataframe


def clean_gcodesnippets(df):
    '''cleans out gcode snippets from dataframe'''
    gcode_df = df.drop(['startingGcode','layerChangeGcode', 'retractionGcode', 'toolChangeGcode', 'endingGcode', 'firmwareTypeOverride'])
    return gcode_df


def choose_main_nozzle(df):
    '''select main nozzle based on chosen setup profile in Simplify3D V4.0 gcode'''
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

