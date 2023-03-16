#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:02:54 2023

@author: JiM in March 2023 
Takes the place of the very-complicated "get_web_driftheader.py".
In an attempt to have one screen of code:
-reads a list of csv data files
-determines if IDs are with "ids_missing_from_header.csv" file (output of update_drift_header.py)
-for each id, gets some fields from a lookup table, and  derives other fields
-outputs simple ORACLE-ready "make_drift_header.out" with many unimportant fileds filled with "nan"
"""
import pandas as pd
import numpy as np
import make_drift_header_functions as mdhf # set of functions used below

dfc=pd.read_csv('deployments_to_add.csv',header=None).drop_duplicates()[0].values #list of cluster file names such as 'drift_fhs_2022_1.csv'
dfm=list(pd.read_csv('ids_missing_from_drift_header_mar2023.dat',header=None).drop_duplicates()[1].values) # list of IDs of interest 
dfi=pd.read_csv('institutes_lookup.csv')

row=[]
institutes=[]# list of codes for the school/lab
col=['ID','LAT_START','LON_START','BTM_DEPTH_START','START_DATE','DROGUE_DEPTH_START','DROGUE_DEPTH_END','DEPLOYER','COMMUNICATION','TYPE','MANUFACTURER','INSTITUTE','PROJECT','DISTANCE',
     'NDAYS','NOTES','SN','ACCURACY','DROGUEDIA','YRDAY0_GMT','END_DATE	','LAT_END','LON_END	','PI','VESSEL']
dfh=pd.DataFrame(columns=col)# empty 
n=np.nan # abbrev for not a number to fill unknown fields
row=[] # row of metadata to be added to with one row per drifter
for k in dfc:
    print(k)
    dfd=pd.read_csv('../web/Drifters/'+k)# reads in a cluster of drifter data
    for j in np.unique(dfd['ID']): # for each drifter in this cluster
        dfd1=dfd[dfd['ID']==j]#this particular drifter
        unders= [i for i, a in enumerate(k) if a == '_']
        institute=k[unders[0]+1:unders[1]].upper()# code for lab/school
        # row to be added to dfh
        if j in dfm: # if this is one of the missing ids in drift_ header, start collecting metadata
            try:
                dfe=mdhf.get_drift(j)
                START_DATE=str(min(dfe['time (UTC)']))
                END_DATE=str(max(dfe['time (UTC)']))
                LAT_START=str(dfe['latitude (degrees_north)'][0])
                LON_START=str(dfe['longitude (degrees_east)'][0])
            except:
                #print('No id='+str(j)+' on NOAA erddap')
                START_DATE,END_DATE,LAT_START,LON_START=n,n,n,n
            institutes.append(institute)
            dfl=dfi[dfi['LAB']==institute]
            #BTM_DEPTH_START=mdhf.get_depth(dfd['LAT'][0],dfd['LON'][0],0.4) #trouble with Python 3.9 not working netCDF4
            BTM_DEPTH_START=n 
            VESSEL=n
            row.append([j,LAT_START,LON_START,BTM_DEPTH_START,START_DATE,n,n,n,'GLOBALSTAR','Irina',institute,institute,n,n,n,n,dfd1['ESN'].values[0],1,1,n,END_DATE,n,n,dfl['PI'].values[0],dfl['VESSEL'].values[0]])
pd.DataFrame(row,columns=col).to_csv('make_drift_header.out')            
            
            
            
#After running this the first time, we added "pi" and "vessel" to the lookup table manually by searching the relavent "index_XXXX.html" file
#dfi=pd.DataFrame(institutes).drop_duplicates()
#dfi.to_csv('institutes_lookup.csv',index=False)