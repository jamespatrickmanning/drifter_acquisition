# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 11:48:53 2013

@author: jmanning
Routine to determine which IDs are in drift_data table but not in drift_header
March 2023 simplified version of an old code "update_drift_header.py"
Assumes you saved some files from ERDDAP servers but it could be rewritten to get dataframes from the ERDDAP sites within this code
"""
import pandas as pd

##########################################
# SOME HARDCODES
mthyr='mar2023' # time of processing (typically once per year)
#filedir='/net/data5/jmanning/drift/'
filedir='/home/user/drift/erddap/'
##########################################

id=pd.read_csv(filedir+'Drifters_All.csv') # this is the distinct ids in Carles ERDDAP 
id_header=list(id['deployment_id'].values)


ids=pd.read_csv(filedir+'drifters.csv')
ids['str_id']=ids['id'].astype(str)
id_data=ids['str_id'].loc[~ids['str_id'].str.startswith('990',0)].astype(int).to_list()# removes GLOBAL drifters

ids_missing_from_drift_header=list(set(id_data)-set(id_header)) 
df1=pd.DataFrame(ids_missing_from_drift_header)  
df1.to_csv(filedir+'ids_missing_from_drift_header_'+mthyr+'.dat') 

ids_missing_from_drift_data=list(set(id_header)-set(id_data))
df2=pd.DataFrame(ids_missing_from_drift_data)  
df2.to_csv(filedir+'ids_missing_from_drift_data_'+mthyr+'.dat')
