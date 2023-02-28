#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 14:41:02 2023

@author: user
"""
case='2023-02-26'
import pandas as pd
#df=pd.read_csv('c:\\users\\DELL\\Downloads\\LiNC_Asset_Status_2020-06-03.csv')
df=pd.read_csv('LiNC Asset Status '+case+'_sorted.csv')
df=df[0:11] # use only the first 241 rows since the others do not have lat/lon
# make all lat and lon floats rather than strings
df['Latitude']=pd.to_numeric(df['Latitude'],downcast="float")
df['Longitude']=pd.to_numeric(df['Longitude'],downcast="float")
# find units in our area
df=df[(df['Latitude']>30.0) & (df['Latitude']<56.0)]
df=df[(df['Longitude']>-89.0) & (df['Longitude']<-62.0)]
print(df['Asset Name'].values)
df.to_csv('uscg_our_area_'+case)