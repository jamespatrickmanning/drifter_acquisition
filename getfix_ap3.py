# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:40:16 2016
-Collects AP3 JSON files on an FTP site and creates _ap3.dat and _ap3.csv files of drifter/mini-boat lat/lon data
-Appends the AP3 data to the data collected by SmartOnes and AP2 units

@author: hxu
with modifications by JiM
Aug 2019 - removed "battery" lines
Jan 2020 - added 2020 option
"""


from matplotlib.dates import date2num
import time
import pytz
import pysftp
import os
from dateutil import parser
import glob
import json
import datetime
import subprocess
import numpy as np
import pandas as pd

def sort_track_by_time(infile): #
  # routine to sort csv file according to id and time
  df=pd.read_csv(infile)
  #df=df[df.ID!='ID'] # gets rid of all header lines except the first
  ids=df.ID.unique() # unique list of ids
  df2=pd.DataFrame()# initialize a new dataframe that will be sorted
  for k in ids:
    df1=df[df.ID==k] # makes a dataframe for just this unit
    df1=df1.drop_duplicates() # gets rid of repeat fixes
    df1=df1.reset_index(drop=True)
    # sort this unit by time but we first need to calculate a datetime
    datet=[]
    year=2000+int(str(df1.ID[0])[0:2])
    for j in range(len(df1)):
      if j>0:
        if float(df1['YEARDAY'][j])-float(df1['YEARDAY'][j-1])<-10: # indicates strattle new year
          year=year+1
          print df1.ID[0],year,df1['YEARDAY'][j],df1['YEARDAY'][j-1]
      datet.append(dt(year,int(df1['MTH'][j]),int(df1['DAY'][j]),int(df1['HR_GMT'][j]),int(df1['MIN'][j])))
    df1=df1.join(DataFrame(datet,columns=['datet']))
    df1=df1.sort_values(by='datet')
    if k==ids[0]:
      df2=df1# add to new dataframe
    else:
      df2=df1.append(df2,ignore_index=True)
  df2.to_csv(infile)
  return

def read_codes_drift():
  # get control file info from /data5/jmanning/drift/codes_ap3.dat
  inputfile1="codes_ap3.dat"
  path1="/net/data5/jmanning/drift/"
  #path1='/home/hxu/Downloads/'
  f1=open(path1+inputfile1,'r')
  esn,case_id,id,depth,boat_pi,school,starttime,endtime,consecutive_batch,project =[],[],[],[],[],[],[],[],[],[]#sep2018
  f1.readline()
  for line in f1:
    print line
    esn.append(line.split()[0])
    case_id.append(line.split()[1])#sep2018
    id.append(line.split()[2])
    depth.append(line.split()[3]) 
    boat_pi.append(line.split()[4])
    school.append(line.split()[5])
    project.append(line.split()[6])
    consecutive_batch.append(line.split()[7]) 
    #starttime.append(parser.parse(line.split()[8]).strftime('%s')) # pre-May 2018
    starttime.append(parser.parse(line.split()[8]).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('UTC')))
    #starttime.append(line.split()[5])
    #endtime.append(datetime.datetime.strptime(line.split()[6],'d%-%b-%Y:%H%M'))
    #endtime.append(parser.parse(line.split()[9]).strftime('%s')) # pre-May 2018
    endtime.append(parser.parse(line.split()[9]).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('UTC')))
    #endtime.append(line.split()[6])

  return esn,id,depth,boat_pi,school,project,starttime,endtime,consecutive_batch,case_id#sep2018
  
# get information associated with each AP3
esn2,ide,depth,boat_pi,school,project,starttime,endtime,consecutive_batch,case_id=read_codes_drift()#sep2018

# remove previous output file
for k in range(len(project)):
  if os.path.exists('/net/pubweb_html/drifter/drift_'+project[k]+'_2016_'+consecutive_batch[k]+'_ap3.dat'): # for now, we are storing ALL ep AP3 data in this 2016 file
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2016_'+consecutive_batch[k]+'_ap3.dat')
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2016_'+consecutive_batch[k]+'_ap3.csv') # uncommented dec 17, 2018 when Cassie noted problem missing Canaries
  elif os.path.exists('/net/pubweb_html/drifter/drift_'+project[k]+'_2017_'+consecutive_batch[k]+'_ap3.dat'): # for now, we are storing ALL ep AP3 data in this 2017 file
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2017_'+consecutive_batch[k]+'_ap3.dat')
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2017_'+consecutive_batch[k]+'_ap3.csv')
  elif os.path.exists('/net/pubweb_html/drifter/drift_'+project[k]+'_2018_'+consecutive_batch[k]+'_ap3.dat'): # for now, we are storing ALL ep AP3 data in this 2018 file
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2018_'+consecutive_batch[k]+'_ap3.dat')
     #os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2018_'+consecutive_batch[k]+'_ap3.csv')
  elif os.path.exists('/net/pubweb_html/drifter/drift_'+project[k]+'_2019_'+consecutive_batch[k]+'_ap3.dat'): # added these on Feb 1, 2019
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2019_'+consecutive_batch[k]+'_ap3.dat')
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2019_'+consecutive_batch[k]+'_ap3.csv')
  elif os.path.exists('/net/pubweb_html/drifter/drift_'+project[k]+'_2020_'+consecutive_batch[k]+'_ap3.dat'): # added these on Jan 14, 2020
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2020_'+consecutive_batch[k]+'_ap3.dat')
     os.remove('/net/pubweb_html/drifter/drift_'+project[k]+'_2020_'+consecutive_batch[k]+'_ap3.csv')

# assumes data from the AssetLink FTP site is already dumped into /home/jmanning/py/backup by another routine "getap3.py"
files=sorted(glob.glob('/home/jmanning/py/backup/*.json'))

esn,date,lat,lon,battery,data_send,meandepth,rangedepth,timelen,meantemp,sdeviatemp=[],[],[],[],[],[],[],[],[],[],[],
c=0
icount=0
date_all=[]
for i in files: # this loops through all the json files in the backup directory and saves any unit that is listed in "codes_ap3.dat"
    if '2016' in i:# or ('2017' in i): # added this on 13 July 2020 to save time but then removed it 10 August when there was evidently trouble Jackalope's first
        continue
    try:
      with open(i) as data_file:    
        data = json.load(data_file)
      if data['momentForward'][0]['Device']['esn'][-6:] in esn2: #make sure that is drifter or miniboat data where "esn2" comes from codes_ap3
         if int(parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date']).strftime('%s')) not in date_all: #make sure that this is not a repeat time
          date=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
          date_all.append(date)    
          #try: # note that we had to add multiple try/except cases since ASSETLINK apparently changed JSON structure a few times in 2017
          try:
                     lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat'] #possibly has problem to read this data
                     lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon']
                     #battery=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['Point']['Battery']
          except:
                     try:
                         lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][3]['PointLoc']['Lat'] #possibly has problem to read this data
                         lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][3]['PointLoc']['Lon']
                         #battery=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['Point']['Battery']
                     except:
                         try:
                           lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lat'] #possibly has problem to read this data
                           lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lon']
                           #battery=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['Point']['Battery']
                         except: # had to add this for Nov 2018 batch of AP3s
                           lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lat'] #possibly has problem to read this data
                           lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lon']
                           #battery=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][7]['Point']['Battery']
          esn=data['momentForward'][0]['Device']['esn']
          yr1=date.year
          mth1=date.month
          day1=date.day
          hr1=date.hour
          mn1=date.minute
          yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))# needed to generate a "yearday" to conform with standard output fields
          datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None) # I don't think this line is needed anymore 5/9/2019                   
		  # added the following line on 6/1/2020 to ignore section of Bobcat miniboat track

          if (str(esn[-6:])=='484660') and ((datet>datetime.datetime(2019,6,8,0,0,tzinfo=None)) and (datet<datetime.datetime(2020,2,21,0,0,tzinfo=None))):
                      continue
          #Liberty		  
          if (str(esn[-6:])=='484980') and ((datet>datetime.datetime(2020,2,24,2,15,tzinfo=None)) and (datet<datetime.datetime(2020,5,29,19,25,tzinfo=None))):
                      continue
          if (str(esn[-6:])=='484980') and ((datet>datetime.datetime(2020,5,30,2,41,tzinfo=None)) and (datet<datetime.datetime(2020,5,30,18,43,tzinfo=None))):
                      continue
          if (str(esn[-6:])=='484980') and ((datet>datetime.datetime(2020,6,12,6,54,tzinfo=None)) and (datet<datetime.datetime(2020,7,22,12,0,tzinfo=None))):
                      continue
          # baot a lahti
          if (str(esn[-6:])=='085940') and ((datet>datetime.datetime(2018,2,12,14,10,tzinfo=None)) and (datet<datetime.datetime(2018,2,14,17,0,tzinfo=None))):
                      continue
          if (str(esn[-6:])=='085940') and ((datet>datetime.datetime(2018,2,23,8,54,tzinfo=None)) and (datet<datetime.datetime(2018,8,30,14,0,tzinfo=None))):
                      continue
          if (str(esn[-6:])=='085940') and ((datet>datetime.datetime(2018,9,5,0,2,tzinfo=None)) and (datet<datetime.datetime(2020,3,6,13,0,tzinfo=None))):
                      continue
          index_idn1=np.where(str(esn[-6:])==np.array(esn2))[0][:] # might return multiple values if ESN is used more than once
          if len(index_idn1)>1: 
                 for k in range(len(index_idn1)):
                    if endtime[index_idn1[k]]>date>starttime[index_idn1[k]]: # made this change 9/19/2018
                       idx=int(index_idn1[k])# this is index of control file associated with this the set of times & esn 
          else:
                    idx=int(index_idn1)
          id_idn1=ide[idx] # where this is the deployment_id associated with this idx case of this time and esn
          # added the following on June 15, 2020
          #Bobcat
          if (str(esn[-6:])=='484660') and (datet>datetime.datetime(2020,2,21,0,0,tzinfo=None)):
                     id_idn1=202471951
          #Boat a Lahti
          if (str(esn[-6:])=='085940') and ((datet>=datetime.datetime(2018,2,14,17,0,tzinfo=None)) and (datet<=datetime.datetime(2018,2,23,9,0,tzinfo=None))):
                     id_idn1=182341192
          if (str(esn[-6:])=='085940') and ((datet>=datetime.datetime(2018,8,30,14,0,tzinfo=None)) and (datet<=datetime.datetime(2018,9,5,0,2,tzinfo=None))):
                     id_idn1=188341191
          if (str(esn[-6:])=='085940') and (datet>=datetime.datetime(2020,3,6,13,0,tzinfo=None)):
                     id_idn1=203341191
          #Liberty
          if (str(esn[-6:])=='484980') and ((datet>=datetime.datetime(2020,5,29,19,0,tzinfo=None)) and (datet<=datetime.datetime(2020,6,12,7,2,tzinfo=None))):
                     id_idn1=205461251
          if (str(esn[-6:])=='484980') and (datet>=datetime.datetime(2020,7,22,12,0,tzinfo=None)):
                     id_idn1=207461251                       
          depth_idn1=-1.0*float(depth[idx]) # made this change 9/21 when the 2nd deployments were not working 
          if (lat<>0.00000) and (lon<>0.00000): # added "lon" to this on 28 Mar 2019
                 project_name=project[idx] # changed this 9/28 from esn2.index(esn[-6:]) to idx
                 idstr=str(id_idn1)
                 yr='20'+idstr[0:2] # generates the year string based on deployment_id
                 consecutive_batch_name=consecutive_batch[idx] # changed this 9/28 from esn2.index(esn[-6:]) to idx
                 if endtime[idx]>date>starttime[idx]: #
                     if not os.path.exists('/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat'):
                          print '/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat'
                          f_output=open('/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat','w').close()
                          f_outcsv=open('/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.csv','w')
                          f_outcsv.write("ID,ESN,MTH,DAY,HR_GMT,MIN,YEARDAY,LON,LAT,DEPTH\n")
                          f_outcsv.close()
                     f_output=open('/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat','a')
                     f_output.write(str(id_idn1).rjust(10)+" "+str(esn[-6:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
    			             str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                     f_output.write(("%11.7f") %(yd1))
                     f_output.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
    			             +str(np.nan)+'\n')
                     f_output.close()        
    			     # csv ouput added May 2016
                     f_outcsv=open('/net/pubweb_html/drifter/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.csv','a')
                     f_outcsv.write(str(id_idn1).rjust(10)+","+str(esn[-6:]).rjust(7)+ ","+str(mth1).rjust(2)+ "," +str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3)+ "," )
                     f_outcsv.write(("%10.7f") %(yd1))
                     f_outcsv.write(","+str(lon).rjust(5)+","+str(lat).rjust(5)+ "," +str(float(depth_idn1)).rjust(4)+"\n")
                     f_outcsv.close()
    except:
        print 'no drifter data in '+ i

# Now loop through the distinct "project" and append this "*_ap3.dat" file to existing .dat file 
unique_projects=list(set(project))
print '***************************'

for k in range(len(unique_projects)):
  print unique_projects[k]
  if unique_projects[k]=='ep':
      #os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_1_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_1.dat')# added this 12/15/2018
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_2_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_2.dat')
      for kk in range(2016,2021):# added 2016 on 4/12/2018 
        os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.dat')
        os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.csv >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.csv')# added 4/9/2018
        #sort_track_by_time('/net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.csv')# added Dec 2019 to fix issues with time being out of order for a few days
      for kk in range(2018,2021):# added 2016 on 4/12/2018, removed 2016 and 2017 on 7/20/2020
        #os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.dat >> /net/pubweb_html/drifter/drift_X.dat')# added 9/18/2019 when not all miniboats showed up in stats
        os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.dat >> /net/pubweb_html/drifter/drift_X.dat')
        dd=pd.read_csv('/net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.csv') #uncommented 6/4/18
        dd.to_csv('new.csv',header=False,index=False)#uncommented 6/4/18
        os.system('cat new.csv >> /net/pubweb_html/drifter/drift_X.csv')#uncommented 6/4/18
  elif unique_projects[k]=='madeira':
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1.dat')
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.csv >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1.csv')
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat >> /net/pubweb_html/drifter/drift_ep_2017_1.dat')
      #os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat >> /net/pubweb_html/drifter/drift_X.dat')
  elif unique_projects[k]=='crmm':
      os.system('cp /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat  /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1.dat')
      os.system('cp /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.csv  /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1.csv')
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat >> /net/pubweb_html/drifter/drift_ep_2017_1.dat')
      #os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2017_1_ap3.dat >> /net/pubweb_html/drifter/drift_X.dat')
      #os.system('cp /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2018_1_ap3.dat  /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2018_1.dat')
      #os.system('cp /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2018_1_ap3.csv  /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2018_1.csv')
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2018_1_ap3.dat >> /net/pubweb_html/drifter/drift_ep_2018_1.dat')
  print 'added _ap3.dat to .dat file and drift_X.dat'
# now run drift2xml on these new .dat files that include both GLOBALSTAR (SmartOne) and IRIDIUM (AP3) results
#pipe1 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2016_1']) # commented out 7/20/2020
#pipe2 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2016_2']) # commented out 7/20/2020
pipe3 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2017_1'])
pipe4 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2018_1'])
pipe4 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2019_1'])# added this feb 1, 2019
pipe41 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2020_1'])# added this jan 14, 2020
pipe42= subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/concant_ep.py'])# added this feb 13, 2019
pipe43= subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/home/jmanning/py/files_by_id.py'])    # added this Apr 1, 2019 and fixed May 8, 2019
pipe5 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_madeira_2017_1'])
pipe6 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_crmm_2017_1'])
os.system('cat /net/pubweb_html/drifter/drift_smcc_2018_1.dat >> /net/pubweb_html/drifter/drift_X.dat') 
os.system('cat /net/pubweb_html/drifter/drift_dick_2019_1.dat >> /net/pubweb_html/drifter/drift_X.dat') 
os.system('cat /net/pubweb_html/drifter/drift_whs_2019_1_ap3.dat >> /net/pubweb_html/drifter/drift_X.dat')
dd=pd.read_csv('/net/pubweb_html/drifter/drift_whs_2019_1_ap3.csv')
dd.to_csv('new.csv',header=False,index=False)
os.system('cat new.csv >> /net/pubweb_html/drifter/drift_X.csv')
pipe7 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/statsd.py'])# switched to order of pipes7-9 when the stats were not picking up some units
pipe71 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/statsd_ep.py']) # added this 24 Sep 2019 since Cassie wasn't seeing all her boats
pipe8 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_X'])
pipe9 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/csv2json.py'])
#pipe91 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/plot_sensor_time_series.py']) # decided to do this in "getap3_sensor.py" instead

