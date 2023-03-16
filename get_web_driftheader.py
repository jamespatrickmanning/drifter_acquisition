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
#from pydap.client import open_url
import numpy as np
###################################
## HARDCODES
#inputfile="/net/data5/jmanning/drift/sqldump_header_mar2020.dat" #derived from running a few programs like "update_drift_header.py" and "getdirft_header.plx"
inputfile="/net/data5/jmanning/drift/sqldump_header_mar2023.dat"
#outputfile="/net/data5/jmanning/drift/drift2header_mar2020.out"
outputfile="drift2header_mar2023.out"
##################################
def read_codes_names(id0):
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="codes.dat"
  path1="/net/data5/jmanning/drift/"
  path1="../"
  f1=open(path1+inputfile1,'r')
  name=''
  lab=''
  depth=999
  for line in f1:
    id=line.split()[1]
    dep=line.split()[2]
    if (int(id)==id0):
      if (len(line.split())>3):# and (float(dep)==0.1):
        depth=line.split()[2]
        name=line.split()[3]
        lab=line.split()[4]
        print(name,lab,depth)
      else:
        lab=''
        name=''
        depth=dep
  f1.close()
  return name,lab,depth

def get_drifter_type(string):
    type_d=''
    drift_type=['irina','cassie','eddie','rachel']
    for i in drift_type:
        if string.lower().find(i)!=-1:
            type_d=i
    if  type_d=='':
        type_d='null'
    return type_d    

#f = urllib.urlopen("http://www.nefsc.noaa.gov/drifter")
#f = urllib.urlopen("http://www.nefsc.noaa.gov/drifter/test_small.html")
f=urllib.request.urlopen("http://studentdrifters.org/tracks/index.html")

#
#f2= open(inputfile)           #you may need to change this path
#data_raw=f2.readlines()
#data_raw_id=[int(data_raw[s][:10]) for s in range(len(data_raw))] # list of  ids missing in header 
data_raw_id=list(pd.read_csv('ids_missing_from_drift_header_mar2023.dat',header=None).drop_duplicates()[1].values) # list of IDs of interest 
n=np.nan
html = f.read() # reads web page
soup = BeautifulSoup(html)
table = soup.find("table")
rows = table.findAll("tr")
soup_all=soup.find_all('a')     # convert html data to 
drift_html=[]
for i in range(len(soup_all)):
    if str(soup_all[i])[:15]=='<a href="drift_': 
       if (str(soup_all[i]).split(">")[0][-3:]=='csv') or (str(soup_all[i]).split(">")[0][-4:-1]=='dat'): # this finds csv file
           drift_html.append(str(soup_all[i]).split(">")[0][9:-1])
    
x = 0
tables=[]
for tr in rows:
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
tables=tables[10:] # get rid of the header line
for kk in range(len(tables)):
    tables[kk]=tables[kk].decode("utf-8")
data_all=[]
data_html=[]
#drift_html=list(set(drift_html))
for i in range(len(drift_html)-1): # JiM added this "-1" in March 2020
    if tables[10*i+7]=='done':     #find the table that we need. 
        #df=pd.read_csv('http://www.nefsc.noaa.gov/drifter/'+drift_html[i])
        #df=pd.read_csv('http://studentdrifters.org/tracks/'+drift_html[i])
        df=pd.read_csv('../'+drift_html[i][:-4]+'.csv')
        if len(df)==0:
            continue
        print(drift_html[i])
        data_all.append(list(df.iloc[0])) # gets the first row
        # now get all the info about this deployment id
        if str(int(df.iloc[0][0])) in tables[10*i+9]:
            for s in tables[10*i+9].split(';'):
                if str(int(list(df.iloc[0])[0])) in s:
                    print('111111111111111111111111111111111111111111111111111111111111111111111')
                    data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1],s])
                    
        else:
            
            data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1],tables[10*i+9]])
        
        for nn in range(1,len(df)):
            if list(df.iloc[nn])[0]!=list(df.iloc[nn-1])[0]: # finds other id 
                data_all.append(list(df.iloc[nn]))
                if str(int(df.iloc[nn][0])) in tables[10*i+9]:
                    for s in tables[10*i+9].split(';'):
                            if str(int(list(df.iloc[nn])[0])) in s:
                                data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1],s])
                else:
                    data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1],tables[10*i+9]])
                #data_html.append([tables[10*i],tables[10*i+1],tables[10*i+2],tables[10*i+3],tables[10*i+4],tables[10*i+5],get_drifter_type(tables[10*i+7]),tables[10*i+8],drift_html[i].split('_')[1]])
lis=[] # distinct ids from the csv file
for x in range(len(data_all)):
    lis.append(int(data_all[x][0]))
num1=0
both_in_lis=[] 

for i in range(len(lis)):
    if lis[i] in data_raw_id: #where data_raw_id come from the sqldump file
        #print 'in sqldump_header: '+str(lis[i])
        both_in_lis.append(lis[i])
        num1+=1
idd,lat_start,lon_start,start_date,end_date,deployer,institute,project,ndays,notes,esn,pi,yrday0_gmt,lat_end,lon_end,dds,dde,dd,depth,drift_type,start_depth,end_depth,manufacturer,sat=[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
dict_data_raw={}
#for q in range(len(data_raw_id)): # for each id we got from sqldump
for p in range(len(data_all)): # for each id we got from data files

        #if lis[p]==data_raw_id[q]: # where "lis" is the integer version of data_all
        if lis[p]==lis[0]:
            idd.append(lis[p])
            '''
            [las,los]=dd2dm(float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[3]),float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[2]))
            lat_start.append(las)
            lon_start.append(los)
            #start_depth.append(round(get_w_depth([float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[2])],[float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[3])])[0][0],1))
            start_depth.append('null')
            #start_date.append(num2date(date2num(dt.datetime(int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[1])+2000,1,1))+float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[2])).strftime("%d-%b-%Y:%H%M"))
            sdate=dt.datetime(int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[8][6:10]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[8][0:2]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[8][3:5]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[8][11:13]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[8][14:16]))
            start_date.append(sdate)
            edate=dt.datetime(int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[9][6:10]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[9][0:2]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[9][3:5]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[9][11:13]),int(data_raw[q][0:data_raw[q].index('\n')].split(' ')[9][14:16]))
            end_date.append(edate)
            ndays.append((edate-sdate).days)
            '''
            lat_start.append(n);lon_start.append(n);start_date.append(n);end_date.append(n);ndays.append(n);start_depth.append(n);end_depth.append(n)
            [pi1,institute1,dep]=read_codes_names(lis[p])
            #pi.append(data_html[p][1].split(' ')[0].split('/')[0])
            #institute.append(data_html[p][0].split(' ')[0].split('/')[0]) 
            pi.append(pi1)
            institute.append(institute1)         
            deployer.append(data_html[p][2])#.split(' ')[0].split('/')[0])
            project.append(data_html[p][8].upper())
            drift_type.append(data_html[p][7].split(' ')[0].split('/')[0])
            #print data_html[p][-1]
            notes.append(data_html[p][-1].replace(",", ";"))
            
            try:
                esn.append(int(data_all[p][1])) # if there is no letters this try will work
                manufacturer.append('null')
                sat.append('GLOBALSTAR')
            except:
                esn.append(data_all[p][1])
                manufacturer.append('null')
                sat.append('GLOBALSTAR')
            #end_date.append(data_raw[q][0:data_raw[q].index('\n')].split(' ')[-2])
            #end_date=n
            #yrday0_gmt.append(sdate.timetuple().tm_yday)
            yrday0_gmt.append(n)
            #[lae,loe]=dd2dm(float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[7]),float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[6]))
            lat_end.append(n)#(lae)
            lon_end.append(n)#(loe)
            
            #d=float(data_raw[q][0:data_raw[q].index('\n')].split(' ')[4])# this gets the mid-depth of the drogue
            d=-1.
            if d>0: 
               d=-1.0*d # make sure drogue depth is negative
            if d==-1.0:
               dds.append('-0.5');dde.append('-1.5');dd.append('1.0')# defines the drogue start depth, end depth, and diameter based on mid-depth
            elif d==-0.2:
               dds.append('-0.0');dde.append('-1.0');dd.append('0.2')# SPOT pipe drifters
            elif d==-0.4:
               dds.append('-0.0');dde.append('-0.4');dd.append('0.5')# UMARYLAND mini drifters
            elif d==-0.5:
               dds.append('-0.0');dde.append('-0.5');dd.append('0.5')# bucket drifters
            elif d<-1.0:
               dds.append(str(d+1.5));dde.append(str(d-1.5));dd.append('1.0')# assumes 3m drogues w/1m diameters
            else:
               dds.append('999');dde.append('999');dd.append('999')# will need to manually edit these 
            depth.append(str(d))
            continue
            
f = open(outputfile, 'w')  
f.writelines('id'+','+'yrday0_gmt'+','+'lat_start'+','+'lon_start'+','+'depth_bottom'+','+'start_date'+','+'drogue_depth_start'+','+'drogue_depth_end'+','+'drogue_diameter'+','+'project'+','+'institute'+','+'pi'+','+'deployer'+','+'type'+','+'manufacturer'+','+'communication'+','+'accuracy'+','+'esn'+','+'yeardays'+','+'notes'+' \n') 
[f.writelines(str(idd[u])+','+str(yrday0_gmt[u])+','+str(float(lat_start[u]))+','+str(float(lon_start[u]))+','+str(start_depth[u])+','+str(start_date[u])+','+dds[u]+','+dde[u]+','+dd[u]+','+project[u]+','+str(institute[u])+','+pi[u]+','+deployer[u]+','+drift_type[u]+','+manufacturer[u]+','+sat[u]+',null,'+str(esn[u])+','+str(ndays[u])+','+str(notes[u])+','+'\n')  for u in range(len(esn)-1,1)]
f.close() 


