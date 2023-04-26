#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 13:16:54 2023

@author: JiM
routine to fix the output of "get_web_driftheader.py" in April 2023 where we needed:
‘'btm_depth_start', 'distance', 'ndays', 'sn', 'droguedia', 'end_date', 'lat_end', 'lon_end', 'vessel'
and we could calculate
 ndays,start_date,end_date,lat_end,lon_end,distance  using drift data on NEFSC erddap
   
"""
import pandas as pd
import netCDF4
import numpy as np
from conversions import dm2dd,dd2dm
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def get_depth(loni,lati,mindist_allowed):
    # routine to get depth (meters) using vol1 from NGDC
    if lati>=40.:
        url='https://www.ngdc.noaa.gov/thredds/dodsC/crm/crm_vol1.nc'
    else:
        url='https://www.ngdc.noaa.gov/thredds/dodsC/crm/crm_vol2.nc'
    nc = netCDF4.Dataset(url).variables 
    lon=nc['x'][:]
    lat=nc['y'][:]
    xi,yi,min_dist= nearlonlat_zl(lon,lat,loni,lati) 
    if min_dist>mindist_allowed:
      depth=np.nan
    else:
      depth=nc['z'][yi,xi]
    return depth#,min_dist

def nearlonlat_zl(lon,lat,lonp,latp): # needed for the next function get_FVCOM_bottom_temp 
    """ 
    used in "get_depth"
    """ 
    # approximation for small distance 
    cp=np.cos(latp*np.pi/180.) 
    dx=(lon-lonp)*cp
    dy=lat-latp 
    xi=np.argmin(abs(dx)) 
    yi=np.argmin(abs(dy))
    min_dist=111*np.sqrt(dx[xi]**2+dy[yi]**2)
    return xi,yi,min_dist


def get_drift(id):
    dfd=pd.read_csv('https://comet.nefsc.noaa.gov/erddap/tabledap/drifters.csvp?id%2Ctime%2Clatitude%2Clongitude%2Cdepth&id=%22'+str(id)+'%22&orderBy(%22time%22)')
    return dfd

ndays,end_date,lat_end,lon_end,distance=[],[],[],[],[]
df=pd.read_csv('drift2header_apr23_test.csv')
#df=df[10:13]# for testing
df = df[df.columns.drop(list(df.filter(regex='Unnamed')))] # gets rid of unwated unnamed columns

# loop through to modify ceratin fields
for k in range(len(df)):    
    if k % 10 ==0:
        print(k)
    lalo=dm2dd(df['lat_start'][k],df['lon_start'][k])
    df.btm_depth_start[k]=f"{get_depth(lalo[1],lalo[0],0.4):.1f}"
    #df.btm_depth_start[k]=np.nan
    try:
        dfd=get_drift(df.id[k])
        dfd['time (UTC)']=pd.to_datetime(dfd['time (UTC)'])
        ndays.append((dfd['time (UTC)'].values[-1]-dfd['time (UTC)'].values[0]).astype('timedelta64[D]')/ np.timedelta64(1, 'D'))
        df.start_date[k]=dfd['time (UTC)'][0].strftime("%d-%b-%y")
        end_date.append(pd.to_datetime(dfd['time (UTC)'].values[-1]).strftime("%d-%b-%y"))
        lalo=dd2dm(dfd['latitude (degrees_north)'].values[-1],dfd['longitude (degrees_east)'].values[-1])
        lat_end.append(lalo[0])
        lon_end.append(lalo[1])
        distance.append(np.nan)
    except:
        ndays.append(np.nan)
        df.start_date[k]=np.nan
        end_date.append(np.nan)
        lat_end.append(np.nan)
        lon_end.append(np.nan)
        distance.append(np.nan)

df['ndays']=ndays
df['end_date']=end_date
df['lon_end']=lon_end
df['lat_end']=lat_end
df.to_csv('drift2header_apr23_fixed.csv')    