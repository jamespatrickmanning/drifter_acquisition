# routine to originally read Dicks miniboat spotmyglobalstar data and put in in raw .csv format
# Modified in April 2022 to read daily position files coming from David Snyder's minidrifters
# Note: See "dick2csv.py" for Oct 2020 version output from Geoforce changed their output format to xls
# 
import pandas as pd
import numpy as np
from datetime import datetime,timedelta

outfile='drift_shp_2022_1'

def parse(datet):
      #dt=datetime.strptime(datet,'%Y-%m-%d %H:%M:%S') # SMCC Global Monitoring format
      dt=datetime.strptime(datet,'%m-%d-%Y %H:%M:%S') # SMCC Global Monitoring format
      return 

#sd=datetime.now()#-timedelta(days=1) # assumes we are processing yesterdays
sd1=datetime(2022,8,21,0,0,0) # start datetime
#sd1=datetime(2022,8,26,0,0,0)
#ed=datetime(2022,6,23,0,0,0) #end
ndays=(datetime.now()-sd1).days+1
d=pd.read_excel('report_'+str(sd1.year)+'-'+str(sd1.month).zfill(2)+'-'+str(sd1.day).zfill(2)+'.xlsx',skiprows=5,sheet_name='Seton_Hall_Prep')#,sheetname='USS Baldwin')
for k in list(range(1,ndays)):
    sd=sd1+timedelta(days=k)
    try:
        d2=pd.read_excel('report_'+str(sd.year)+'-'+str(sd.month).zfill(2)+'-'+str(sd.day).zfill(2)+'.xlsx',skiprows=5,sheet_name='SHP_STEM')
    except:
        print('no seton_hall on ',sd)
    try:
        d3=pd.read_excel('report_'+str(sd.year)+'-'+str(sd.month).zfill(2)+'-'+str(sd.day).zfill(2)+'.xlsx',skiprows=5,sheet_name='SHP_Pirates')
    except:
        print('no SHP_Pirates on ',sd)            
    try:
        d=pd.concat([d, d2, d3], ignore_index=True)
    except:
        print('not all three')
ts=pd.to_datetime(d['Date'],format='%m/%d/%Y %H:%M')
d=d[ts.notnull()]
ts=ts[ts.notnull()]

id,newESN,la,lo,datet,yd,yr,mth,day,hr,mn=[],[],[],[],[],[],[],[],[],[],[]
for k in range(len(d)):
  lalo=d['Lat/Lng'][k].split(',')
  #la.append(float(lalo[0][1:-1]))
  #lo.append(float(lalo[1][:-2]))
  la.append(float(lalo[0]))
  lo.append(float(lalo[1]))
  datet.append(ts[k])
  yd.append(ts[k].timetuple().tm_yday+ts[k].timetuple().tm_hour/24.)
  yr.append(ts[k].timetuple().tm_year)
  mth.append(ts[k].timetuple().tm_mon)
  day.append(ts[k].timetuple().tm_mday)
  hr.append(ts[k].timetuple().tm_hour) 
  mn.append(ts[k].timetuple().tm_min)

  if d['Asset'][k]=='SHP_Elizabeth':
    id.append('224400691')
    newESN.append(4511733) #2679081
  elif d['Asset'][k]=='USS Miller':
    id.append('195360602')
    newESN.append(2679081) 
  elif d['Asset'][k]=='Seton_Hall_Prep':
    id.append('225501441')
    newESN.append(4512473)
  elif d['Asset'][k]=='SHP_STEM':
    id.append('228400691')
    newESN.append(3356081)
  elif d['Asset'][k]=='SHP_Pirates':
    id.append('228400692')
    newESN.append(3362619)
  else:
    id.append('99999999')
    newESN.append(777777)
d2=pd.DataFrame()  
d2['datet']=datet
d2['ESN']=newESN
d2['ID']=id
d2['depth']=[0.1]*len(d2)
d2['yearday']=yd
d2['year']=yr
d2['mth']=mth
d2['day']=day
d2['hr']=hr
d2['mn']=mn
d2['lon']=lo
d2['lat']=la
d2['temp']=['nan']*len(d2)
'''
header=['ID','ESN','month','day','hour','minute','yearday','lon','lat','depth','temp','year']
df=pd.DataFrame([d2.ID[:].values,d2.ESN[:].values,d2.mth[:].values,d2.day[:].values,d2.hr[:].values,d2.mn[:].values,d2.yearday[:].values,d2.lon[:].values,d2.lat[:].values,d2.depth[:],d2.temp[:],d2.year[:]])
df=df.transpose()
df.columns=header
df=df.sort_values(['ID','year','month','day','hour','minute'])
'''
header=['ID','ESN','MTH','DAY','HR_GMT','MIN','YEARDAY','LON','LAT','DEPTH','TEMP','YEAR']
df=pd.DataFrame([d2.ID[:].values,d2.ESN[:].values,d2.mth[:].values,d2.day[:].values,d2.hr[:].values,d2.mn[:].values,d2.yearday[:].values,d2.lon[:].values,d2.lat[:].values,d2.depth[:],d2.temp[:],d2.year[:]])
df=df.transpose()
df.columns=header
df=df.sort_values(['ID','YEAR','MTH','DAY','HR_GMT','MIN'])
df.to_csv(outfile+'.csv',index=False)
df=df.drop('YEAR',1)
df.to_csv(outfile+'.dat',sep=' ',index=False,header=False)

