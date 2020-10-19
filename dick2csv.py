# routine to read Dicks miniboat spotmyglobalstar data and put in in raw .csv format
# Modified in Oct 2020 when Geoforce changed their output format to xls
# brought code down to Toshiba laptop including drift2xml.py
import pandas as pd
import numpy as np
from datetime import datetime,timedelta

def parse(datet):
      #dt=datetime.strptime(datet,'%Y-%m-%d %H:%M:%S') # SMCC Global Monitoring format
      dt=datetime.strptime(datet,'%m-%d-%Y %H:%M:%S') # SMCC Global Monitoring format
      return 

#d1=pd.read_excel('/net/data5/jmanning/drift/dick/PositionReport.xlsx',skiprows=5) # append to this first month
#d2=pd.read_excel('/net/data5/jmanning/drift/dick/PositionReport.xlsx',skiprows=5,sheetname='USS Miller')
#d3=pd.read_excel('/net/data5/jmanning/drift/dick/PositionReport.xlsx',skiprows=5,sheetname='Sailing on a Dream')
#d=pd.concat([d1, d2], ignore_index=True)
# now get the automated daily files starting with start day (sd) May 17
'''
  try:
    d4=pd.read_excel('/net/data5/jmanning/drift/dick/report_'+str(sd.year)+'-'+str(sd.month).zfill(2)+'-'+str(sd.day).zfill(2)+'.xlsx',skiprows=5,sheetname='USS Baldwin')
    d5=pd.read_excel('/net/data5/jmanning/drift/dick/report_'+str(sd.year)+'-'+str(sd.month).zfill(2)+'-'+str(sd.day).zfill(2)+'.xlsx',skiprows=5,sheetname='USS Miller')
    try:
      d6=pd.read_excel('/net/data5/jmanning/drift/dick/report_'+str(sd.year)+'-'+str(sd.month).zfill(2)+'-'+str(sd.day).zfill(2)+'.xlsx',skiprows=5,sheetname='Sailing on a Dream')
      if d6['Date'][0]>datetime(2019,7,6,16,0,0):
        d=pd.concat([d, d4, d5, d6], ignore_index=True)
      else:
        d=pd.concat([d, d4, d5], ignore_index=True)
    except:
      d=pd.concat([d, d4, d5], ignore_index=True)
  except:
    print sd
'''
d=pd.read_excel('Miniboat Research Collaborative-Asset Movement - Excel.xls',skiprows=8)    
#sd=sd+timedelta(days=1)

ts=pd.DatetimeIndex(d['Date'])
d=d[ts.notnull()]
ts=ts[ts.notnull()]
id,newESN,la,lo,datet,yd,yr,mth,day,hr,mn=[],[],[],[],[],[],[],[],[],[],[]
for k in range(len(d)):
  print(d['Last Location'][k])  
  lalo=d['Last Location'][k].split(',')
  if lalo[0][0:1]!='(':
      continue
  la.append(float(lalo[0][1:-1]))
  lo.append(float(lalo[1][:-2]))  
  datet.append(ts[k])
  yd.append(ts[k].timetuple().tm_yday+ts[k].timetuple().tm_hour/24.)
  yr.append(ts[k].timetuple().tm_year)
  mth.append(ts[k].timetuple().tm_mon)
  day.append(ts[k].timetuple().tm_mday)
  hr.append(ts[k].timetuple().tm_hour) 
  mn.append(ts[k].timetuple().tm_min)

  '''  
  if d['Asset'][k]=='USS Baldwin':
    id.append('195360601')
    newESN.append(2674948) #2679081
  elif d['Asset'][k]=='USS Miller':
    id.append('195360602')
    newESN.append(2679081) 
  else: #d['Asset'][k]=='Sailing on a Dream'
    id.append('196360601')
    newESN.append(281289)
  '''
  id.append('200430691')
  newESN.append('3203054')
d2=pd.DataFrame()  
d2['datet']=datet
d2['ESN']=newESN
d2['ID']=id
d2['depth']=[0.1]*len(d2)
#d=d[d.ID != 'NaN'] # get rid of all units without ID assigned
#d['yearday']=d.datet.dayofyear+d.datet.hour/24.0+d.datet.minute/(24.0 * 60)
d2['yearday']=yd
d2['year']=yr
d2['mth']=mth
d2['day']=day
d2['hr']=hr
d2['mn']=mn
d2['lon']=lo
d2['lat']=la
d2['temp']=['nan']*len(d2)
d2=d2[d2.datet>datetime(2020,10,9,22,0,0)]
#d=d[d.lat>40]
#d=d.loc[(d['Asset']=='Sailing on a Dream') & (d['datet']>dt(2019,6,30,0,0,0)),:]# 
header=['ID','ESN','month','day','hour','minute','yearday','lon','lat','depth','temp','year']
df=pd.DataFrame([d2.ID[:].values,d2.ESN[:].values,d2.mth[:].values,d2.day[:].values,d2.hr[:].values,d2.mn[:].values,d2.yearday[:].values,d2.lon[:].values,d2.lat[:].values,d2.depth[:],d2.temp[:],d2.year[:]])
df=df.transpose()
df.columns=header
df=df[df.lat[:].values>5.0] # band aid rids of some bad points in Nov 2015
df=df.sort_values(['ID','year','month','day','hour','minute'])
#df.to_csv('/net/pubweb_html/drifter/drift_smcc_'+year+'_1.csv',index=False)
df.to_csv('drift_dick_2020_1.csv',index=False)
# now make the .dat format for "drift2xml.py" to work on it
df=df.drop('year',1)
#df.to_csv('/net/pubweb_html/drifter/drift_smcc_'+year+'_1.dat',sep=' ',index=False,header=False)
df.to_csv('drift_dick_2020_1.dat',sep=' ',index=False,header=False)

