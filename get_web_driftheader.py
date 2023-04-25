# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 13:05:56 2015
After you get file 'sqldump_header.dat', run this python program to get a dat file split by comma.
Note: Made an alternative version of this in March 2023 called "make_drift_header.py" but not sure which is best

@author: hxu
Modified by JiM in late 2017 
Modified by JiM in March 2023 to work on studentdrifters.org/tracks and Python 3.9
"""
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import datetime as dt
from matplotlib.dates import num2date,date2num
import sys
#sys.path.append("/home3/ocn/jmanning/py/mygit/modules/")
from conversions import distance,dm2dd,dd2dm
from get_web_driftheader_functions import read_codes_names,get_drifter_type#,get_depth
#from pydap.client import open_url
import numpy as np
###################################
## HARDCODES
#inputfile="/net/data5/jmanning/drift/sqldump_header_mar2020.dat" #derived from running a few programs like "update_drift_header.py" and "getdirft_header.plx"
inputfile="/net/data5/jmanning/drift/sqldump_header_mar2023.dat"
#outputfile="/net/data5/jmanning/drift/drift2header_mar2020.out"
outputfile="drift2header_mar2023.out"
##################################
#f = urllib.urlopen("http://www.nefsc.noaa.gov/drifter")
f = urllib.request.urlopen("http://studentdrifters.org/tracks/index.html")
#f = urllib.request.urlopen("file:/home/user/drift/web/Drifters/index_2021.html")

data_raw_id=list(pd.read_csv('ids_missing_from_drift_header_mar2023.dat',header=None).drop_duplicates()[1].values) # list of IDs of interest 
n=np.nan
html = f.read() # reads web page
soup = BeautifulSoup(html,features="html.parser")
table = soup.find("table")
rows = table.findAll("tr")
soup_all=soup.find_all('a')     # convert html data to 
drift_html=[]
for i in range(len(soup_all)):
    if str(soup_all[i])[:15]=='<a href="drift_': 
        if  ('_ep_' not in str(soup_all[i])) and  ('_dick_' not in str(soup_all[i])) and ('cfcc' not in str(soup_all[i])) and ('madeira' not in str(soup_all[i])) and ('crmm' not in str(soup_all[i])):# and ('_tes_' not in str(soup_all[i])):  #excludes miniboats
            if (str(soup_all[i]).split(">")[0][-4:-1]=='csv') or (str(soup_all[i]).split(">")[0][-4:-1]=='dat'): # this finds csv file
                drift_html.append(str(soup_all[i]).split(">")[0][9:-1])
    
x = 0
tables=[]
for tr in rows:
  if ('Educational Passages' not in str(tr)) and ('sailboats' not in str(tr)):
    cols = tr.findAll("td")
    if not cols: 
        # when we hit an empty row, we should not print anything to the workbook
        continue
    y = 0
    for td in cols:
        texte_bu = td.text
        texte_bu = texte_bu.encode('utf-8')
        texte_bu = texte_bu.strip()
        tables.append(texte_bu)
#tables=tables[10:] # get rid of the header line
for kk in range(len(tables)):
    tables[kk]=tables[kk].decode("utf-8")
data_all=[]
data_html=[]
for i in range(len(drift_html)-1): # JiM added this "-1" in March 2020
    if (tables[10*i+7]=='done') or (tables[10*i+7]=='underway'):     #find the table that we need. 
        try:
            df=pd.read_csv('../'+drift_html[i][:-4]+'.csv')
        except:
            try:
                df=pd.read_csv('../web/Drifters/'+drift_html[i][:-4]+'.csv')
            except:
                try:
                    df=pd.read_csv('https://studentdrifters.org/tracks/'+drift_html[i][:-4]+'.csv')
                except:
                    print('No data available for '+drift_html[i])
                    continue
        if len(df)==0:
            continue
        if len(df.columns)==11: # this is the case where index is included 
            df=df.drop('Unnamed: 0',axis=1)
        print(drift_html[i])
        data_all.append(list(df.iloc[0])) # gets the first row of drifter data for this first drifter
        # now get all the info about this deployment id
        if str(int(df.iloc[0]['ID'])) in tables[10*i+9]:
            for s in tables[10*i+9].split(';'):
                if str(int(df.iloc[0]['ID']))in s:
                    print('111111111111111111111111111111111111111111111111111111111111111111111')
                    data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),s])
                    
        else:
            
            data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+9]])
        
        for nn in range(1,len(df)):
            #if list(df.iloc[nn])[1]!=list(df.iloc[nn-1])[1]: # finds other id 
            if df['ID'][nn]!=df['ID'][nn-1]: # finds other id 
                data_all.append(list(df.iloc[nn]))
                #if str(int(df.iloc[nn][1])) in tables[10*i+9]:
                if str(int(df['ID'][nn])) in tables[10*i+9]:
                    for s in tables[10*i+9].split(';'):
                            #if str(int(list(df.iloc[nn])[1])) in s:
                            if str(int(df['ID'][nn])) in s:
                                data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),s])
                else:
                    data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+9]])
                #data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1]])
lis=[] # distinct ids from the csv file
for x in range(len(data_all)):
    lis.append(int(data_all[x][0]))
num1=0
both_in_lis=[] 

'''
for i in range(len(lis)):
    if lis[i] in data_raw_id: #where data_raw_id come from the sqldump file
        #print 'in sqldump_header: '+str(lis[i])
        both_in_lis.append(lis[i])
        num1+=1
'''
idd,lat_start,lon_start,start_date,end_date,deployer,institute,project,ndays,notes,esn,pi,yrday0_gmt,lat_end,lon_end,dds,dde,dd,depth,type,start_depth,end_depth,manufacturer,sat=[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
dict_data_raw={}
for p in range(len(data_all)): # for each id we got from data files

        #if lis[p]==data_raw_id[q]: # where "lis" is the integer version of data_all
            #idd.append(lis[p])
            idd.append(int(data_all[p][0]))
            la=data_all[p][8]
            lo=data_all[p][7]
            [las,los]=dd2dm(la,lo)
            lat_start.append('%8.2f' % las)
            lon_start.append('%8.2f' % los)
            start_date.append(n);end_date.append(n);ndays.append(n);start_depth.append(n);end_depth.append(n);yrday0_gmt.append(n)
            lat_end.append(n);lon_end.append(n)
            [pi1,institute1,dep]=read_codes_names(int(data_all[p][0]))
            if pi1=='': # case where we get some info from html rather than codes.dat
               pi.append(data_html[p][1]) 
               institute.append(data_html[p][0])
               manufacturer.append(data_html[p][0])
            else:       # case where we found info in codes.dat
               pi.append(pi1)
               institute.append(institute1) 
               manufacturer.append(institute1)
            deployer.append(data_html[p][2])
            project.append('null')#data_html[p][8].upper())
            notes.append(data_html[p][-1].replace(",", ";"))
            esn.append(int(data_all[p][1])) # if there is no letters this try will work
            sat.append('GLOBALSTAR')
            d=data_all[p][9]
            if d>0: 
               d=-1.0*d # make sure drogue depth is negative
            if d==-1.0:
               dds.append('-0.5');dde.append('-1.5');dd.append('1.0');type.append('Irina')# defines the drogue start depth, end depth, and diameter based on mid-depth
            elif d==-0.2:
               dds.append('-0.0');dde.append('-1.0');dd.append('0.2');type.append('Pipe')# SPOT pipe drifters
            elif d==-0.4:
               dds.append('-0.0');dde.append('-0.4');dd.append('0.2');type.append('Mini')# UMARYLAND mini drifters
            elif d==-0.5:
               dds.append('-0.0');dde.append('-0.5');dd.append('0.25');type.append('Bucket')# bucket drifters
            elif d<-1.0:
               dds.append(str(d+1.5));dde.append(str(d-1.5));dd.append(str(d));type.append('drogue')# assumes 3m drogues w/1m diameters
            else:
               dds.append('999');dde.append('999');dd.append('999');type.append('unknown')# will need to manually edit these 
            depth.append(str(d))
            continue
            
f = open(outputfile, 'a')  
#f.writelines('id'+','+'yrday0_gmt'+','+'lat_start'+','+'lon_start'+','+'depth_bottom'+','+'start_date'+','+'drogue_depth_start'+','+'drogue_depth_end'+','+'drogue_diameter'+','+'project'+','+'institute'+','+'pi'+','+'deployer'+','+'type'+','+'manufacturer'+','+'communication'+','+'accuracy'+','+'esn'+','+'yeardays'+','+'notes'+' \n') 
for u in range(len(esn)):
    f.writelines(str(idd[u])+','+str(yrday0_gmt[u])+','+lat_start[u]+','+lon_start[u]+','+str(start_depth[u])+','+str(start_date[u])+','+dds[u]+','+dde[u]+','+dd[u]+','+project[u]+','+str(institute[u])+','+pi[u]+','+deployer[u]+','+type[u]+','+manufacturer[u]+','+sat[u]+',null,'+str(esn[u])+','+str(ndays[u])+','+str(notes[u])+','+'\n')
f.close() 


