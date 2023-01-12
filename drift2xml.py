"""
routine to reformat "drift_20XX.dat" to xml
where "X" is the number of days to plot prior to now

save the xml to webserver or some temp location as filename.xml


Created on Wed Sep 21 11:46:45 2011
@author: xiuling.wu

Modified by JiM 4 Oct 2012
- allowed "filename" as argument
Modified by JiM 18 June 2019
- allowed multiple legs of AP3
Modified by Jim 7 May 2021
- look in /drifter folder
Modified by JiM 7 July 2021
- remove duplicate fixes
Modified by JiM 30 May 2022
- fix double quote appearing in html
Modified by JiM 15 Nov 2022
- allow for Cassie's miniboat track
Modified by Jim in Dec 2022
- generate a drift_X.csv file w/miniboat tracks too
"""
import csv
import sys
import time
import ftplib
from utilities import lat2str, lon2str
from datetime import *
from matplotlib.dates import date2num,num2date
import numpy as np
import pandas as pd
#hardcode
ageactive=1
# open output and input file
filedirection='/home/user/drift/' # while testing on laptop
#filedirection='/net/pubweb_html/drifter/'
#filedirection='/drifter/'

def eMOLT_cloud(ldata):# send file to SD machine
        # function to upload a list of files to SD machine
        for filename in ldata:
            # print u
            session = ftplib.FTP('66.114.154.52', 'huanxin', '123321')
            file = open(filename, 'rb')
            #session.cwd("/BDC")
            #session.cmd("/tracks")
            # session.retrlines('LIST')               # file to send
            session.storbinary("STOR " + filename.split('/')[-1], fp=file)  # send the file
            # session.close()
            session.quit()  # close file and FTP
            #time.sleep(1)
            file.close()
            print(filename.split('/')[-1], 'uploaded in SD endpoint')
            
def read_codes_names(esn0,id0):
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="/home/user/drift/codes.dat"
  #path1="/net/data5/jmanning/drift/"
  path1=""
  f1=open(path1+inputfile1,'r')
  for line in f1:
    esn=line.split()[0]
    id=line.split()[1]
    dep=line.split()[2]
    if (esn==esn0) and (id==id0):
      if (len(line.split())>3):# and (float(dep)==0.1):
        depth=line.split()[2]
        name=line.split()[3]
        lab=line.split()[4]
        #print name,lab,depth
      else:
        lab=''
        name=''
        depth=dep
  f1.close()
  '''
  try: # if it is not in "codes.dat", it should be in "codes_ap3.dat"
    name
  except NameError:
    inputfile1="codes_ap3.dat"
    f1=open(path1+inputfile1,'r')
    for line in f1:
      esn=line.split()[0]
      if esn!="ESN": # case of the header line
        #print esn,esn0,id,id0
        id=line.split()[2]
        dep=line.split()[3]
        if (esn==esn0) and (id==id0):
          if (len(line.split())>3):# and (float(dep)==0.1):
            depth=line.split()[3]
            name=line.split()[4]
            lab=line.split()[5]
            print(name,lab,depth)
          else:
            lab=''
            name=''
            depth=dep
  '''
  try: # 
     name
  except:
     name=''
     lab=''
     depth=1.0
  return name,lab,depth
  #return esn, id,depth

filename=sys.argv[1]
fid=open(filedirection+filename+'.xml','w')
ireader = csv.reader(open(filedirection + filename+'.dat', "r"))

#raw data loaded
idss,esn,yeardays_all,lat_all,lon_all,day_all,mth_all,hr_all,mn_all,dep_all,nan_all=[],[],[],[],[],[],[],[],[],[],[]
# if the first line is comment line, skip
for line in (x for x in ireader if x[0][0] !='%'):
    #print line
    idss.append(line[0].split()[0])
    esn.append(line[0].split()[1])
    yeardays_all.append(line[0].split()[6])
    lat_all.append(line[0].split()[8])
    lon_all.append(line[0].split()[7])
    day_all.append(line[0].split()[3])
    mth_all.append(line[0].split()[2])
    hr_all.append(line[0].split()[4])
    mn_all.append(line[0].split()[5])
    dep_all.append(line[0].split()[9])
    #nan_all.append(line[0].split()[10])
    nan_all.append(np.nan)



# convert string to float
yeardays_all=[float(i)+1 for i in yeardays_all]# in python num2date(), less one day than matlab, so add 1 here
lat_all=[float(i) for i in lat_all]
lon_all=[float(i) for i in lon_all]

if (sys.argv[1]=='drift_whs_2022_1') or (sys.argv[1]=='drift_X') or (sys.argv[1]=='drift_fhs_2022_1'): # here is where we are adding miniboat track from Cassie
    if (sys.argv[1]=='drift_whs_2022_1') or (sys.argv[1]=='drift_X'):
        df=pd.read_csv('https://educationalpassages.org/wp-content/uploads/csv/LadyLance_1.csv')
    elif (sys.argv[1]=='drift_fhs_2022_1') or (sys.argv[1]=='drift_X'):
        df1=pd.read_csv('https://educationalpassages.org/wp-content/uploads/csv/Riptide_7.csv')
        df2=pd.read_csv('https://educationalpassages.org/wp-content/uploads/csv/Rock_Star_2.csv')
        df=pd.concat([df1,df2],ignore_index=True)
    df['moment_date']=pd.to_datetime(df['moment_date'])
    for k in range(len(df)):
        if (df['deployment_id'][k]==220410701):
           df['deployment_id'][k]='220410705' 
           esn.append('9999998')
        elif df['deployment_id'][k]==220410703:
            df['deployment_id'][k]='220410706' 
            esn.append('9999997')
        elif df['deployment_id'][k]==220390701:
            df['deployment_id'][k]='220390702'
            esn.append('9999999')           
        idss.append(df['deployment_id'].values[k])
        yeardays_all.append(float(df['moment_date'][k].timetuple().tm_yday)+df['moment_date'][k].hour/24.+df['moment_date'][k].minute/60/24.)
        lat_all.append(float(df['latitude'][k]))
        lon_all.append(float(df['longitude'][k]))
        day_all.append(df['moment_date'][k].day)
        mth_all.append(df['moment_date'][k].month)
        hr_all.append(df['moment_date'][k].hour)
        mn_all.append(df['moment_date'][k].minute)
        dep_all.append(-0.1)
        nan_all.append('nan')
        
    # now make a new ".csv" file with this miniboat track added
    dfcsv=pd.DataFrame({'ID':idss,'ESN':esn,'MTH':mth_all,'DAY':day_all,'HR_GMT':hr_all,'MIN':mn_all,'YEARDAY':yeardays_all,'LON':lon_all,'LAT':lat_all,'DEPTH':dep_all})
    if sys.argv[1]=='drift_whs_2022_1':
        dfcsv.to_csv(filedirection+'drift_whs_2022_1.csv')
    elif sys.argv[1]=='drift_fhs_2022_1':
        dfcsv.to_csv(filedirection+'drift_fhs_2022_1.csv')
    else:
        dfcsv.to_csv(filedirection+'drift_X.csv')
ids=list(set(idss))# list of distinct ids
#print ids
# write the first line of the xml output file
fid.write('<?xml version="1.0" encoding="UTF-8"?>\n<markers>\n')

# setup a set of line colors
#cc=['#FFFFFF','#33FFCC','#FF0000','#f5f5f5','#FF66FF','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC','#FFFF33',
cc=['#FFFFFF','#33FFCC','#FF0000','#9acd32','#800080','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC','#FFFF33',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57','#f5f5f5',
    '#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57','#f5f5f5',
    '#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#99CC66','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57',
    '#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff',
    '#FF0000','#f5f5f5','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57','#f5f5f5',
    '#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57','#f5f5f5',
    '#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff',
    '#FF0000','#99CC66','#3333CC','#FF66FF','#660033','#FFFF33','#33FFCC','#990066','#9900FF','#FFCC33','#9966CC','#33FFFF','#FF00CC',
    '#2e8b57','#99CC66','#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff','#2e8b57',
    '#f5f5f5','#fa8072','#008080','#9acd32','#800080','#dda0dd','#ffa500','#000080','#48d1cc','#ff00ff']
cc=cc+cc# doubles the size

nowtime=date2num(datetime.now())
if sys.argv[1]!='drift_X':
  maxtime=0
else:
  maxtime=date2num(date.today()-timedelta(days=30))
    
# for each drifter write out line and marker         
for k in range(len(ids)): # loop through all the distinct deployment ids
    idesn=np.where(np.array(idss)==ids[k])[0] # finds the index of all rows with this id
    esnthis=esn[idesn[0]]
    year=int('20'+ids[k][0:2])
    lat,lon,time,yeardays,depth,temp=[],[],[],[],[],[]
    for i in range(len(idss)): # loop through entire dat file
        if idss[i]==ids[k]: # for this distinct id
            lat.append(lat_all[i])
            # JiM added the following two lines in Jan 2019 because DPAT tool apparently needed Longtiude west
            if lon_all[i]>0:
               lon_all[i]=lon_all[i]-360.
            lon.append(lon_all[i])
            yeardays.append(yeardays_all[i]) 
            if len(yeardays)>1:
              if yeardays[-1]<200 and yeardays[-2]>250 and ids[k]!=164400721 and ids[k]!=1754107030: # triggers a new year
                year=year+1
            if (int(mth_all[i])==2) and (int(day_all[i])==29): # trouble with no accepting leap year date in Feb 2016
               day_all[i]=28    
            time.append(date2num(num2date(yeardays_all[i]).replace(year=year).replace(month=int(mth_all[i])).replace(day=int(day_all[i]))))
    ind=sorted(range(len(time)), key=lambda k: time[k]) # find indexes sort by time
    time=[time[i] for i in ind]
    lon=[lon[i] for i in ind]
    lat=[lat[i] for i in ind]
    # here is where we want to get rid of duplicate fixes by a) make dataframe, b) drop repeats, and c) export time,lat,and lon
    
    df=pd.DataFrame(np.array([time,lat,lon]).transpose())
    df=df.drop_duplicates()
    time=list(df[0].values)
    lat=list(df[1].values)
    lon=list(df[2].values)
    #print('len(lon)='+str(len(lon)))
    if ids[k]=='175320743':
         print(ids[k],esnthis,num2date(time[-1]))
    if time[-1]>maxtime:    
      last_drifter_time=time[-1]
      if nowtime-last_drifter_time > ageactive:
        active=0
      else:
        active=1  
      if esnthis=='995664':#West
        active=0
      fid.write('<line width="3" color="'+cc[k]+'">\n')
      for i in range(len(lat)):
        if np.isnan(lat[i])==False and time[i]>maxtime:
            fid.write('<point lat="'+str(lat[i])+'" lng="'+str(lon[i])+'"/>\n')
      fid.write('</line>\n')
      [boatName,schoolName,depth]=read_codes_names(esnthis,ids[k])
      la=lat2str(round(lat[-1],2))
      lo=lon2str(round(lon[-1],2))
      if ids[k]=='195360601':
          boatName='USS_Baldwin'
          schoolname='United_Tech_Center_Bangor_ME'
      elif ids[k]=='195360602':
          boatName='USS_Miller'
          schoolName='United_Tech_Center_Bangor_ME'
      elif ids[k]=='200400651':
          boatName='Alexander_3'
          schoolName='United_Tech_Center_Bangor_ME'
          depth=0.1
      elif ids[k]=='224400691':
          boatName='SHP_Elizabeth'
          schoolName='Seton_Hall_Prep'
          depth=0.2
      elif ids[k]=='226400691':
          boatName='SHP_STEM'
          schoolName='Seton_Hall_Prep'
          depth=0.2      #print float(depth)
      if (float(depth)==0.1) or (float(depth)==0):
        '''
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Unmanned SailBoat: &lt;strong&gt;'+boatName+ '&lt;/strong&gt; &lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
        '''
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Unmanned SailBoat: &lt;strong&gt;'+boatName+ '&lt;/strong&gt; &lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la)+' '+str(lo)
        +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
        +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
        +' GMT\n"/>')
      elif float(depth)==0.05: #case of drogued drifter that evidently lost its drogue
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="surface float only&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      elif float(depth)==0.2:
        ''' 
        fid.write('<marker lat='+str(lat[-1])+' lng='+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Mini Surface Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
        '''
        fid.write('<marker lat='+'"'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Mini Surface Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+la[0:2]+' '+la[4:8]+'N '+lo[0:2]+' '+lo[4:8]+'W '
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
     
      elif float(depth)==0.3:
        '''    
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Wooden Loggerhead Turtle Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
        '''
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Wooden Loggerhead Turtle Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la)+' '+str(lo)
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      elif float(depth)==0.4:
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Mini Surface Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      elif float(depth)==0.5:
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Bucket Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      elif abs(float(depth))==1.0:
        '''
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Surface Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
        '''
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Surface Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la)+' '+str(lo)
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      elif float(depth)>1.0:
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="Drogued Drifter&lt;br&gt; School Name: '+schoolName+'&lt;br&gt; ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      else:
        fid.write('<marker lat="'+str(lat[-1])+'" lng="'+str(lon[-1])+'" label="'+str(ids[k])+'" active="'+str(active)+
              '" html="ID = '+str(ids[k])+' ESN = '+str(esnthis)+'&lt;br&gt; Position:'+str(la.encode("ascii","ignore"))+' '+str(lo.encode("ascii","ignore"))
              +'&lt;br&gt;'+'StartTime='+num2date(time[0]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')+' GMT &lt;br&gt; EndTime='
              +num2date(time[-1]).replace(tzinfo=None).strftime('%m/%d/%Y %H:%M')
              +' GMT\n"/>')
      

if (sys.argv[1]=='drift_grnms_2014_1') | (sys.argv[1]=='drift_grnms_2015_2'):
      fid.write('<line width="3" color="black">\n')
      fid.write('<point lat="31.421064" lng="-080.9212"/>\n')
      fid.write('<point lat="31.421064" lng="-080.828145"/>\n')
      fid.write('<point lat="31.362732" lng="-080.828145"/>\n')
      fid.write('<point lat="31.362732" lng="-080.9212"/>\n')
      fid.write('<point lat="31.421064" lng="-080.9212"/>\n')
      fid.write('</line>\n')
if sys.argv[1]=='drift_gomi_2014_1':
     fid.write('<marker lat="43.1768" lng="-70.4432" label="ESP-1"  html="ESP-1" />\n') 
     fid.write('<marker lat="43.6872" lng="-69.9768" label="ESP-2"  html="ESP-2" />\n') 
     fid.write('<marker lat="43.8029" lng="-69.4575" label="ESP-3"  html="ESP-3" />\n') 
if sys.argv[1]=='drift_fa_2014_1':
     fid.write('<marker lat="41.945" lng="-70.578333" label="Plymouth Nuclear"  html="Plymouth Nuclear Power Plant" />\n') 
fid.write('</markers>')
fid.close()
# send these output files to the StudentDrifter FTP drop
eMOLT_cloud([filedirection+filename+'.dat',filedirection+filename+'.csv',filedirection+filename+'.xml'])
