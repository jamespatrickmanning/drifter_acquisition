# -*- coding: utf-8 -*-
"""
modified by JiM 3 Oct 2011
- simplified axtrack_getfix_example.py to this
- changed hardcoded directories
- added call to "getfix.plx" and "confirmfix.plx" using subprocess
- delimited by startyd and endyd (datetime objects)

modified by JiM in Dec 2014 and Jun 2015
- run on the COMET machine 

modified by JiM in Nov 2015 
- added csv output

modified by JiM in Apr 2019
"""
import sys
#hardcode path of modules
#hardcode path of input (1) and output data (2) 
path1="/net/data5/jmanning/drift/"
#path2="/var/www/html/ioos/drift/"
path2="/net/drifter/"
#path2="/net/data5/jmanning/drift/"
inputfile="raw2013.dat"

from matplotlib.dates import date2num
import time
from getfix_functions import *
import subprocess
import datetime
import numpy as np #1

def trans_latlon(string):
    #if string[2]=='0' and string[3]=='0':
    #    string=string[0:2]+string[4:]    
    lat=0.000010728836*int('0x'+string[4:10],16)
    lon=-0.000021457672*(16777216-int('0x'+string[10:16],16))
    #print lat,lon
    return lat,lon

# get "including" (ESNs), "startyd", and "endyd" for this case using getfix_function "get
print sys.argv[1]
[including,caseid,startyd,endyd]=getwplot(sys.argv[1]) # function within the "getfix_functions" module
print str(len(including))+' drifters'
#example: 
#including=[320241, 322134, 328420, 368537, 327192, 368742]
#caseid=[1, 1, 1, 1, 1, 1] # consecutive use of this transmitter
# get "id" and "depth" for specific ESNs from /data5/jmanning/drift/codes.dat
#[esn,ide,depth,lab,name]=read_codes()
[esn,ide,depth]=read_codes()
# update the raw datafile by running perl routine getfix.plx
if sys.argv[1]=='drift_2013.dat':
  pipe = subprocess.Popen(["perl", "/home/jmanning/drift/getfix_soap.plx"])
f_output=open(path2+str(sys.argv[1]),'w')

# add csv output
basename=str(sys.argv[1])
basename=basename[0:-4]+'.csv'
f_outcsv=open(path2+basename,'w')
f_outcsv.write("ID,ESN,MTH,DAY,HR_GMT,MIN,YEARDAY,LON,LAT,DEPTH\n")

for i in range(len(including)):
  #open the raw input datafile 
  f = open(path1+inputfile,'r') 

  # Next: some special cases where we want to put header or deployment info at top of file
  #  if sys.argv[1]=='drift_cscr_2014_1.dat':
  #     f_output.write("ID        ESN   MTH DAY HR_GMT MIN  YEARDAY    LON           LAT     DEPTH TEMP\n")
  #if including[i]==996317:
  #    f_output.write(' 137430662  996317  7  4  16   0 184.6        -65.74115  43.52900 -1.0 nan\n')

  #start parsing the variables needed from the raw datafile
  for line in f:
      if line[1:4]=='stu' and len(line)>95:
        pid=line[59:95] # get "packet ID" needed to confirm reciept later in the program
      if line[1:4]=='esn':
        if ((line[7]=='1') or (line[7]=='3')) and (line[13]!='<'): #7-digit SmartOne transmitter modified this line in May 2019 to accept the new Solar Smartones starting with "3"  
          idn1=int(line[7:14])# ESN number
        elif line[11]=='<': #AP2s!!
          idn1=int(line[7:11])
        else:            #6-digit TrackPack
          idn1=int(line[7:13]) 
        if idn1==including[i]:
                # check to see if this esn is listed in "codes.dat", so I can not find it's id and depth
                index_idn1=np.where(str(idn1)==np.array(esn))[0]
                if index_idn1.shape[0]<>0:
                    #print idn1,caseid,index_idn1
                    id_idn1=int(ide[index_idn1[caseid[i]-1]])
                    depth_idn1=-1.0*float(depth[index_idn1[caseid[i]-1]])
                    #lab1=lab[index_idn1[caseid[i]-1]]
                    #name1=name[index_idn1[caseid[i]-1]]
                    skip1=next(f) #skip one line
                    if skip1[1:9]=="unixTime":
                        #if including[i]==321764:#id_idn1==110410711:
                        #  print 't2',index_idn1.shape[0],caseid[i],index_idn1[caseid[i]-1],id_idn1,idn1,yd1,startyd[i],endyd[i],mth1,day1
                        unixtime=int(skip1[10:20]) #get unix time
                        #convert unixtime to datetime
                        time_tuple=time.gmtime(unixtime)
                        yr1=time_tuple.tm_year
                        mth1=time_tuple.tm_mon
                        day1=time_tuple.tm_mday
                        hr1=time_tuple.tm_hour
                        mn1=time_tuple.tm_min
                        skip2=next(f) # skip one line
                        skip3=next(f)
                        if skip3[7:12]=='track':#determines what type of format
                            trackpack='yes'
                        else:
                            trackpack=' no'
                        if skip3[1:8]=='payload': # case of AP2, for example, where we only have hexidecimal lat/lon
                               yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                               datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None)
                               if datet>startyd[i] and datet<endyd[i]:
                                   data_raw=skip3[47:67]
                                   #print data_raw
                                   lat,lon=trans_latlon(data_raw)
                                   if lat < 89.: # this stops north pole data from being added
                                       lastime= str(mth1).rjust(2)+ " " + str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)
                                       f_output.write(str(id_idn1).rjust(10)+" "+str(idn1).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                          str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                       f_output.write(("%10.7f") %(yd1))
                                       f_output.write("  "+str(round(lon,5))+' '+str(round(lat,5))+ "   " +str(float(depth_idn1)).rjust(4)+ " "
                                          +str(np.nan)+'\n')
                        skip4=next(f)
                        if (skip4[2:7]=='SeqNo') and (skip3[7:12]<>'maint'):
                            next(f)
                            next(f)
                            skip5=next(f)
                            if skip5[2:9]=='Message': skip6=next(f)
                            if (skip6[2:7]<>'Power') and (skip6[2:7]<>'TriesP'): 
                                if skip6[2:9] =='Message': 
                                    skip6=next(f)
                                if  skip6[2:9]=='Battery':   
                                    skip6=next(f)
                                if  skip6[2:9] =='GPSData':   
                                    skip6=next(f)
                                if skip6[2:9] =='MissedA': 
                                    skip6=next(f)
                                if skip6[2:9] =='GPSFail': 
                                    skip6=next(f)
                                yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                                datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None)                               
                                if datet>startyd[i] and datet<endyd[i]:    
                                    if skip6[12]<>"N" and skip6[2:5]<>'Lat' and skip6[12]<>'a' and skip6[12]<>'p' and skip6[12]<>'u':
                                        if skip6[12]<>'-':
                                            try:
                                              lon=float(skip6[12:20])
                                            except:
                                                print skip6[12:20],idn1
                                        else:    
                                            lon=float(skip6[12:21])
                                        if lon>-180:# and lat>-50):# had to add this condition for one case of esn 950263 in Mar 2013   
                                        #if (lon<10) and (lon>-180):# and lat>-50):# had to add this condition for one case of esn 950263 in Mar 2013   
                                          skip7=next(f)
                                          try:
                                             lat=float(skip7[11:19])
                                          except:
                                             print skip7[11:19],idn1,datet   
                                          if lat>-50: # had to add this as -20 in the case of esn 995417 in Feb 2016 when it kep reporting from south pacific but then changed it to -50 in Dec 2019
                                              lastime= str(mth1).rjust(2)+ " " + str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)
                                              f_output.write(str(id_idn1).rjust(10)+" "+str(idn1).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                              str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                              f_output.write(("%10.7f") %(yd1))
                                              f_output.write(" "+str(lon).rjust(10)+' '+str(lat).rjust(10)+ " " +str(float(depth_idn1)).rjust(4)+ " "
                                              +str(np.nan)+'\n')
                                              # csv ouput added Nov 2015
                                              f_outcsv.write(str(id_idn1).rjust(10)+","+str(idn1).rjust(7)+ ","+str(mth1).rjust(2)+ "," +
                                              str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3)+ "," )
                                              f_outcsv.write(("%10.7f") %(yd1))
                                              f_outcsv.write(","+str(lon).rjust(10)+","+str(lat).rjust(10)+ "," +str(float(depth_idn1)).rjust(4)+"\n")
  f.close()
# special case where you want to add recovery position
if including[i]==733225:
      f_output.write(' 145420703  733225  5  28  12  31 184.6        -70.013  41.9919 -1.0 nan\n')
f_output.close()
f_outcsv.close()

# confirm getting the data using confirmfix.plx
var = str(pid)
#print 'pid='+var
#print lastime
if sys.argv[1]=='drift_2013.dat':
  pipe2 = subprocess.Popen(["perl", "/home/jmanning/drift/confirmfix.plx",var])
  #statsd
#subprocess.Popen(["rm","/home3/ocn/jmanning/py/temp.dat"])
noext=sys.argv[1]
#if sys.argv[1]=='drift_sbnms_2012_1.dat':
#    pipe3 = subprocess.Popen(['python','/home3/ocn/jmanning/py/getgts.py'])
#    pipe4 = subprocess.Popen(['python','/home3/ocn/jmanning/py/drift2xml_aoml.py',noext[:-4]])
if (sys.argv[1]!='drift_ep_2016_2.dat') and (sys.argv[1]!='drift_X.dat') and  (sys.argv[1]!='drift_ep_2017_1.dat') and (sys.argv[1]!='drift_ep_2018_1.dat') and (sys.argv[1]!='drift_ep_2019_1.dat') and (sys.argv[1]!='drift_ep_2020_1.dat'): # these are done AFTER Iridium data is added on the EMOLT machine
  if sys.argv[1]=='drift_ep_2012_1.dat': 
    pipe4 = subprocess.Popen(['/anaconda/bin/python','/home/jmanning/drift/drift2xml_ep.py',noext[:-4]])
  else:
    pipe4 = subprocess.Popen(['/anaconda/bin/python','/home/jmanning/drift/drift2xml.py',noext[:-4]])  
#  if sys.argv[1]=='drift_2013.dat':
#    pipe5 = subprocess.Popen(['/anaconda/bin/python','/home/jmanning/drift/statsd.py'])
