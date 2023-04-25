#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 13:16:54 2023

@author: JiM
routine to fix the output of "get_web_driftheader.py" in April 2023 where we needed:
‘'btm_depth_start', 'distance', 'ndays', 'sn', 'droguedia', 'end_date', 'lat_end', 'lon_end', 'vessel'
and we could calculate
 ndays,start_date,end_date,ndays,lat_end,lon_end,distance  using drift data on NEFSC erddap
   
"""
import pandas as pd
import netCDF4
import numpy as np
from conversions import dm2dd
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

def dm2dd(lat,lon):
    """
    convert lat, lon from decimal degrees,minutes to decimal degrees
    """
    (a,b)=divmod(float(lat),100.)   
    aa=int(a)
    bb=float(b)
    lat_value=aa+bb/60.

    if float(lon)<0:
        (c,d)=divmod(abs(float(lon)),100.)
        cc=int(c)
        dd=float(d)
        lon_value=cc+(dd/60.)
        lon_value=-lon_value
    else:
        (c,d)=divmod(float(lon),100.)
        cc=int(c)
        dd=float(d)
        lon_value=cc+(dd/60.)
    return lat_value, -lon_value

def get_drift(id):
    dfd=pd.read_csv('https://comet.nefsc.noaa.gov/erddap/tabledap/drifters.csvp?id%2Ctime%2Clatitude%2Clongitude%2Cdepth&id=%22'+str(id)+'%22&orderBy(%22time%22)')
    return dfd
ndays=[]
df=pd.read_csv('drift2header_apr23.csv')
df = df[df.columns.drop(list(df.filter(regex='Unnamed')))] # gets rid of unwated unnamed columns

# loop through to modify ceratin fields
for k in range(3):#len(df)):
    lalo=dm2dd(df['lat_start'][k],df['lon_start'][k])
    df.btm_depth_start[k]=get_depth(lalo[1],lalo[0],0.4)
    dfd=get_drift(df.id[k])
    dfd['time (UTC)']=pd.to_datetime(dfd['time (UTC)'])
    ndays.append(dfd['time (UTC)'][-1]-dfd['time (UTC)'][0])
    df.start_date[k]=dfd['time (UTC)'][0].strftime("%d-%b-%y")
    df.end_date[k]=dfd['time (UTC)'][0].strftime("%d-%b-%y")
    