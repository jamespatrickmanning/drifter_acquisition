# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:40:16 2016
-Collects AP3 JSON files on an FTP site and creates _ap3.dat and _ap3.csv files of drifter/mini-boat lat/lon data
-Appends the AP3 data to the data collected by SmartOnes and AP2 units

@author: hxu
with modifications by JiM
"""


from matplotlib.dates import date2num
import time
import pytz
#import pysftp
import os
from dateutil import parser
import glob
import json
import datetime
import subprocess
import numpy as np
import pandas as pd
import spreadsheet_final as gs

def read_codes_drift(): # reads old control file
  """get control file info from /data5/jmanning/drift/codes_ap3.dat"""
  inputfile1="codes_ap3.dat"
  path1="/net/data5/jmanning/drift/"
  #path1='/home/hxu/Downloads/'
  f1=open(path1+inputfile1,'r')
  esn,case_id,id,depth,boat_pi,school,starttime,endtime,consecutive_batch,project =[],[],[],[],[],[],[],[],[],[]#sep2018
  f1.readline()
  for line in f1:
    print(line)
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

  return [esn,id,depth,boat_pi,school,project,starttime,endtime,consecutive_batch,case_id]#sep2018

def read_codes_drift_2(): # reads googlesheet metadata
    """ grabs meta data from drift_headers google sheet """
    data_dict = gs.getfix_ap3_gs_data()
    ide = data_dict["id"]
    esn = data_dict["esn"]
    case_id = data_dict["case_id"]
    starttime = data_dict["start_date"]
    endtime = data_dict["end_date"]
    depth = data_dict["drogue_depth"]
    boat_pi = data_dict["boat_pi"]
    school = data_dict["school"]
    consecutive_batch = data_dict["consecutive_batch"]
    project = data_dict["project_names"]
    
    gs.write_ap3_codes_file(data_dict)

    return [esn, ide, depth, boat_pi, school, project, starttime, endtime, consecutive_batch, case_id]
    # return ide, esn, case_id, starttime, endtime, depth, boat_pi, school, consecutive_batch, project


def combine_meta_data():
    """ combines meta data from control file and google sheet """
    control_data = read_codes_drift()
    google_sheet_data = read_codes_drift_2()
    print(google_sheet_data)

    for category_index, elt in enumerate(control_data):
        google_sheet_data[category_index] = google_sheet_data[category_index] + elt

    print(google_sheet_data)

    return google_sheet_data


# get information associated with each AP3
esn2, ide, depth, boat_pi, school, project, starttime, endtime, consecutive_batch, case_id = combine_meta_data()



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

# assumes data from the AssetLink FTP site is already dumped into /home/jmanning/py/backup by another routine "getap3.py"
files=sorted(glob.glob('/home/jmanning/py/backup_test/*.json'))

esn,date,lat,lon,battery,data_send,meandepth,rangedepth,timelen,meantemp,sdeviatemp=[],[],[],[],[],[],[],[],[],[],[],
c=0
icount=0
date_all=[]
for i in files: # this loops through all the json files in the backup directory and saves any unit that is listed in "codes_ap3.dat"
    try:
      with open(i) as data_file:
        data = json.load(data_file)
      if data['momentForward'][0]['Device']['esn'][-6:] in esn2: #make sure that is drifter or miniboat data
         if int(parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date']).strftime('%s')) not in date_all: #make sure that this is not a repeat time
                  date=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                  date_all.append(date)
                  esn=data['momentForward'][0]['Device']['esn']
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
		  
                  yr1=date.year
                  mth1=date.month
                  day1=date.day
                  hr1=date.hour
                  mn1=date.minute

                  yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))# needed to generate a "yearday" to conform with standard output fields
                  datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None) # I don't think this line is needed anymore 5/9/2019
		  #data_send=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'] # commented this line in April 2019 when I realized it was not needed
                  try:
                      # the following several lines added in Sep 2018
                      index_idn1=np.where(str(esn[-6:])==np.array(esn2))[0][:] # might return multiple values if ESN is used more than once
                      if len(index_idn1)>1:
                        for k in range(len(index_idn1)):
                           if endtime[index_idn1[k]]>date>starttime[index_idn1[k]]: # made this change 9/19/2018
                             idx=int(index_idn1[k])# this is index of control file associated with this the set of times & esn
                      else:
                         idx=int(index_idn1)
                      id_idn1=ide[idx] # where this is the deployment_id associated with this idx case of this time and esn
                      depth_idn1=-1.0*float(depth[idx]) # made this change 9/21 when the 2nd deployments were not working
                      if (lat!=0.00000) and (lon!=0.00000): # added "lon" to this on 28 Mar 2019 AND CHANGED <> TO != FOR PYTHON 3
                          project_name=project[idx] # changed this 9/28 from esn2.index(esn[-6:]) to idx
                          if (project_name=='madeira') or (project_name=='crmm'):
                             if (id_idn1==182461231) or (id_idn1==182461237) or (id_idn1==188271151):
                               yr='2018'
                             else:
                               yr='2017'
                             consecutive_batch_name='1'
			     #print project_name
                          else:
                             idstr=str(id_idn1)
                             yr='20'+idstr[0:2] # generates the year string based on deployment_id
			     #consecutive_batch_name=consecutive_batch[esn2.index(esn[-6:])]
                             consecutive_batch_name=consecutive_batch[idx] # changed this 9/28 from esn2.index(esn[-6:]) to idx
                          if (id_idn1==182461231) and (mth1==2) and (day1==25) and (hr1==18): # bandaid made 3/11/2019 to remove bad Comcomly point fixed 5/23/2019
                           pass
                          else:
                           if (id_idn1==193320801) and (lon>0.):                              # bandaid made 3/28/2019 to remove bad Ashley Hall points
                             print('bad fix')
                           else:
                             if endtime[idx]>date>starttime[idx]: #
			      #print project_name
                              if not os.path.exists('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat'):
                                  print('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat')
                                  f_output=open('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat','w').close()
                                  f_outcsv=open('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.csv','w')
                                  f_outcsv.write("ID,ESN,MTH,DAY,HR_GMT,MIN,YEARDAY,LON,LAT,DEPTH\n")
                                  f_outcsv.close()
                              f_output=open('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.dat','a')
                              f_output.write(str(id_idn1).rjust(10)+" "+str(esn[-6:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                 str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                              f_output.write(("%11.7f") %(yd1))
                              f_output.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
			              +str(np.nan)+'\n')
                              f_output.close()
			      # csv ouput added May 2016
                              f_outcsv=open('/net/pubweb_html/drifter/test/drift_'+project_name+'_'+yr+'_'+consecutive_batch_name+'_ap3.csv','a')
                              f_outcsv.write(str(id_idn1).rjust(10)+","+str(esn[-6:]).rjust(7)+ ","+str(mth1).rjust(2)+ "," +str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3)+ "," )
                              f_outcsv.write(("%10.7f") %(yd1))
                              f_outcsv.write(","+str(lon).rjust(5)+","+str(lat).rjust(5)+ "," +str(float(depth_idn1)).rjust(4)+"\n")
                              f_outcsv.close()

                              '''
                              if (esn[-6:]=='085940') or (esn[-6:]=='379700') or (esn[-6:]=='314280'): # this is the special case of crmm and madeira needing to be added to ep_2018
			        f_output=open('/net/pubweb_html/drifter/test/drift_ep_2018_1_ap3.dat','a')
			        f_output.write(str(id_idn1).rjust(10)+" "+str(esn[-6:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
			              str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
			        f_output.write(("%11.7f") %(yd1))
			        f_output.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
			              +str(np.nan)+'\n')
			        f_output.close()
			        # csv ouput added May 2016
			        f_outcsv=open('/net/pubweb_html/drifter/test/drift_ep_2018_1_ap3.csv','a')
			        f_outcsv.write(str(id_idn1).rjust(10)+","+str(esn[-6:]).rjust(7)+ ","+str(mth1).rjust(2)+ "," +str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3)+ "," )
			        f_outcsv.write(("%10.7f") %(yd1))
			        f_outcsv.write(","+str(lon).rjust(5)+","+str(lat).rjust(5)+ "," +str(float(depth_idn1)).rjust(4)+"\n")
			        f_outcsv.close()
                               ''' #commented out the block above 9 May 2019 and made all "crmm" to "ep"


                  except:
                      pass
    except:
        print('no drifter data in '+ i)

# Now loop through the distinct "project" and append this "*_ap3.dat" file to existing .dat file
unique_projects=list(set(project))
print('***************************')
'''
for k in range(len(unique_projects)):
  print unique_projects[k]
  if unique_projects[k]=='ep':
      #os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_1_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_1.dat')# added this 12/15/2018
      os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_2_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_2016_2.dat')
      for kk in range(2016,2020):# added 2016 on 4/12/2018
        os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.dat >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.dat')
        os.system('cat /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1_ap3.csv >> /net/pubweb_html/drifter/drift_'+unique_projects[k]+'_'+str(kk)+'_1.csv')# added 4/9/2018
      for kk in range(2016,2020):# added 2016 on 4/12/2018
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

pipe1 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2016_1'])
pipe2 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2016_2'])
pipe3 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2017_1'])
pipe4 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2018_1'])
pipe4 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_ep_2019_1'])# added this feb 1, 2019
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
#os.system('cat /net/pubweb_html/drifter/drift_whs_2019_1_ap3.csv >> /net/pubweb_html/drifter/drift_X.csv')
pipe7 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/drift2xml.py','drift_X'])
pipe8 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/csv2json.py'])
pipe9 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/statsd.py'])
#pipe91 = subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/plot_sensor_time_series.py']) # decided to do this in "getap3_sensor.py" instead
'''
