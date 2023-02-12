# -*- coding: utf-8 -*-
"""
Created on Mon Feb 6 05:40:32 2023
@author: JiM 

Note: This is a simplified version of "old_fixfix.py"  
"""

## STEPS ARE AS FOLLOWS:
#    - load all the ascii data file from one cluster
#    - for each drifter it conducts 6 basic steps
#    - eliminate repeat times
#    - calculate forward and backward differences (velocity) and eliminate bad points
#    - writes meta data to log file
#    - check for drogue loss
#    - clean plots of track (pth) and velocity uv_id_final.png)
#    - generates oracle ready ascii file
##################################################################################################
import os
import conda
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ['PROJ_LIB'] = '/home/user/anaconda3/pkgs/proj-8.2.1-h277dcde_0/share'
from  conversions import ll2uv_datetime#To convert from longitude/latitude to unit vectors
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.dates import num2date,date2num, DateFormatter
import os
import pandas as pd
import matplotlib.dates as mdates
from pylab import *


####HARDCODES############################
lab='glerl'
yearstr='2022'
consec='1' # batch of drifters this year
processbatch='feb2022' # process session to name file which documents ids processed
critfactor=8 #multiple of the mean velcity to discard
minla=-20;maxla=70;minlo=-150;maxlo=0  # delimiting data to make it easier (we probably will not change this ever)
bathy=True # set to "True" if isobaths are wanted
depcont=[-100] # depth contour in final plot (apparently not used in 5/2012)
timetoedit=15 #number of seconds to click on bad points (set to 20 first run through)
strattle=0 # this will eventually flag to "1" if yeardays change by more than 365
input_format='csv' #dat is the usual format
input_dir='/home/user/drift/' # input file directory
outdir_base='/home/user/drift/process/output/'
plotdir="/home/user/drift/process/plots/" # directory where the final plots are stored
##END HARDCODES###############################################

####### DEFINE INPUT AND OUPUT BASED ON HARDCODES ABOVE AND OPEN SOME LOG FILES TO APPEND TO########################
# open some files
outdir=outdir_base+lab+'/'+yearstr
fn='drift_'+lab+'_'+yearstr+'_'+consec+'.'+input_format
print('processing '+fn)
al=pd.read_csv(outdir_base+'already_loaded_ids.dat','r') # how do we create this file? see 'drift_cookbook'
fido=open(outdir+'/prep_for_oracle_'+fn[6:],'w') # OPENS OUPUT FILE
fidids=open(outdir_base+"drift2header_"+processbatch+".dat","w") # list of ids processed needed for making header
fid=open(outdir_base+"drift.log","w")#permanent log file that is appended to../home3/ocn/jmanning/drift/drift.log
fid.write('\n'+'#'*40+' below is '+str(fn)+' log '+'#'*40+'\n') # start new section in log file
if not os.path.exists(outdir): os.makedirs(outdir)
#year=int(fn.split('_')[2])# assumes the year appears in the filename after the first two underscores
year=int(yearstr)
year1=year # this does not get incremented
### END DEFINING FILES AND VARIABLES ################################################


########## FUNCTIONS  ###############
def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)
    return np.argmin(dist_2)

def textxy(y1,x1,y2,x2,c):
    x3=(y2-y1)*c/(np.sqrt(np.square(x2-x1)+np.square(y2-y1)))
    y3=(x2-x1)*c/(np.sqrt(np.square(x2-x1)+np.square(y2-y1)))
    return y3,-x3
######  end  functions ###############################

######  MAIN PROGRAM BEGINS ####################
#raw data loaded
df=pd.read_csv(input_dir+fn)
df['temps']=['nan' for i in range(len(df))]# creates "temps" since some input files do not have a temps column
ids=np.sort(list(set(df.ID)))

for k in range(len(ids)): #where "ids" is a sorted list of distinct ids and int latitude, longitude, time
  # check to see if this id was already loaded into ORACLE
  fid.write('Drifter '+str(ids[k])+'\n')
  print('\n\n')
  print('Processing '+str(ids[k]))
  if size(where(al==ids[k]))==0: # where "al" is the "already_loaded_ids.dat" file stored in the "prep_ora" directory
    strattle=0
    year=year1 # assumes all units from this batch start at the same year
    df1=df[df.ID==ids[k]]
    #generate a datetime column
    datet=[]
    for i in range(len(df1)):
        if (i>1):# here's where we account for a new year
            if df1.YEARDAY[i]-df1.YEARDAY[i-1]<-200:
                year=year+1
                print('incremented year to '+str(year))
                strattle=1
        datet.append(dt(year,df1.MTH[i],df1.DAY[i],df1.HR_GMT[i],df1.MIN[i]))
    df1['datet']=datet
    print("there are ", len(df1.LAT), "original fixes for id =",ids[k])    

    # STEP 1a: check for repeat time
    orig=len(df1)# original length of df1
    df1.drop_duplicates(inplace=True)
    numdupl=str(orig-len(df1))
    print('There are '+numdupl+' removed.')
    fid.write('   '+numdupl+' points deleted with the same times'+'\n')
    df1.drop_duplicates(inplace=True)
    
    
    if len(df1)>2: # continue if there is more than one fix
     ### Calculate u & v component of velocity
     u,v,spd,jdn=ll2uv_datetime(df1.datet.values,df1.LAT.values,df1.LON.values)# was yeardays but now uses "time" as of 3/29/2012

     # STEP 1b: look at histogram of u & v to check for outliers visually
     #fig=plt.figure(1)
     kw = dict(histtype='stepfilled', alpha=0.5)#, normed=True)
     fig, (ax0, ax1) = plt.subplots(ncols=2, sharex=True, sharey=True)
     ax0.hist(u, **kw)
     ax1.hist(v, **kw)
     _ = ax1.set_title('v')
     _ = ax0.set_title('u')
     thismanager = plt.get_current_fig_manager()
     thismanager.window.setGeometry(0,0,900,500)
     

     # check for drifter going aground (ie very low velocity)
     idlow=list(np.where(np.array(spd)<float(np.mean([abs(i) for i in spd]))/100)[0])#calculate ids where velocity is less that 100 times the mean and print warning of "grounding"
     if idlow!=[]:
        for i in range(len(idlow)):
            print('WARNING: Drifter ',str(ids[k]),' may be hung up on gear or aground on ',str(jdn[idlow[i]]),' where velocity is < 1# mean')

     #### find bad velocities where criteria was just calculated
     # calculate a reasonable criteria for this drifter
     crit=np.mean([abs(i) for i in spd])*critfactor
     print("\n Velocity criteria set to ", str(critfactor),' times the mean or ',str(crit),' cm/s')
     idbadf=list(np.where(abs(np.array(spd))>crit)[0])
     #we want to remove these bad points from df1
     df1.drop(idbadf,axis=0,inplace=True)
       

     # remove bad points based on speed plot
     idgood=len(df1)
     fig=plt.figure(2)
     plt.plot(pd.to_datetime(jdn),spd)
     plt.plot(pd.to_datetime(jdn),spd,marker="o",markerfacecolor="r",linestyle='None')
     fig.autofmt_xdate()
     thismanager = plt.get_current_fig_manager()
     thismanager.window.setGeometry(0,800,1500, 500)
     plt.title(str(ids[k])+' resultant velocity')
     plt.show()
     print('\n Click on any obviously bad velocities and then press the enter key. You have '+str(timetoedit)+' seconds.')
     badpoints=ginput(n=0,timeout=timetoedit)
     print('badpoints = ',badpoints)#,timeout=10)
     index_badpoints=[]
     plt.close(fig)
     badpoints_num=len(badpoints)
     if badpoints_num!=0:
       for i in range(badpoints_num):
           index_badpoints.append(closest_node(badpoints[i], tuple(zip(date2num(jdn),spd))))  # get closest point in 2 dimensions
       print(index_badpoints )    
       print("%10.2f percent bad velocities deleted according to manual clicks on velocity" % float(float(badpoints_num)/len(df1)*100.))
       df1.drop(df1.index[index_badpoints],axis=0,inplace=True)
      
     # remove bad points between two clicks after redrawing time series plot
     fig=plt.figure(3)
     fu2,fv2,spd2,jd2=ll2uv_datetime(df1.datet.values,df1.LAT.values,df1.LON.values)
     plt.plot(pd.to_datetime(jd2),spd2,'mo-',markersize=5)#marker='o',markerfacecolor="r",linestyle='None')
     fig.autofmt_xdate()
     thismanager = plt.get_current_fig_manager()
     thismanager.window.setGeometry(0,800,1500, 500)        
     plt.title(str(ids[k]))
     plt.show()     
     del_between=input('Do you want to delete all the points between two points? [default n]') or "n"
     if del_between=="Y" or del_between=="y" :
          print("Please click the first bad point and the last bad point to choose the range of the bad points")
          thismanager = plt.get_current_fig_manager()
          between_badpoints=ginput(n=2)
          index_between_badpoints=[]
          for i in range(len(between_badpoints)):
              index_between_badpoints.append(int(np.interp(between_badpoints[i][0],date2num(jd2),range(len(jd2)))))
          index_betweens=[]
          for i in range(sorted(index_between_badpoints)[0],sorted(index_between_badpoints)[1]+1):
              index_betweens.append(i)
          del_between_badpoints=sorted(index_between_badpoints)[1]-sorted(index_between_badpoints)[0]+1
          badpoints_num=len(badpoints)+del_between_badpoints
          print("%10.2f percent editted due to bad velocities from manual clicks between two points" % float(float(badpoints_num)/len(df1)*100.))
          df1.drop(df1.index[index_betweens],inplace=True)
     plt.close(fig)
     
     # redraw time series plot
     fig=plt.figure(4)
     fu3,fv3,spd3,jd3=ll2uv_datetime(df1.datet.values,df1.LAT.values,df1.LON.values)
     #plot_speed(jd3,spd3)
     plt.plot(pd.to_datetime(jd3),spd3,'bo-')  
     fig.autofmt_xdate()
     thismanager = plt.get_current_fig_manager()
     #thismanager.window.SetPosition((2000, 0))
     thismanager.window.setGeometry(0,800,900, 500)     
     plt.title(str(ids[k])+' resultant velocities after edits')
     plt.ylabel('cm/s')# added 6/4/2019 without testing
     plt.show()
     print('\n replotted velocity ... pausing for '+str(timetoedit)+' seconds')
     pause(timetoedit)

     #step 5a:
     #manually delete points based on track where we zoom into each bad point noted in first clciks
     fig=plt.figure(5)
     plt.plot(df1.LON.values,df1.LAT.values,'ro-')
     thismanager = plt.get_current_fig_manager()
     thismanager.window.setGeometry(1000,0,900, 800)     
     plt.title(str(ids[k])+' track AFTER edits')
     plt.show()
     #del_between=input('\n Do you want to delete the points? [default n]') or "n"
     del_between='n'
     badplotpts=[] 
     if del_between=="Y" or del_between=="y":
       print('click on any obviously bad points and then press the enter key on the track. You have '+str(timetoedit)+' seconds.')
       bad=ginput(n=0,timeout=timetoedit)
       print(bad)
       badplotpts=[] #index of points that are found to be near the same index of x & y
       if len(bad)>0:
         for kbad in range(len(bad)):
           fig=plt.figure(7)
           plt.plot(df1.LON,df1.LAT,'ro-')
           ylim(bad[kbad][1]-.1,bad[kbad][1]+.1)
           xlim(bad[kbad][0]-.1,bad[kbad][0]+.1)
           thismanager = plt.get_current_fig_manager()
           thismanager.window.setGeometry(50,100,640, 545)
           plt.show()
           print('click on any obviously bad points and then press the enter key. You have '+str(timetoedit)+' seconds.')
           bad1=ginput(n=1,timeout=timetoedit)
           badplotpts.append(closest_node(bad1, zip(lon,lat)))
       ylim(min(lat),max(lat))
       xlim(min(lon),max(lon))
       print('# bad pts'+str(len(badplotpts)))
       for kj in badplotpts:
           plt.plot(df1.LON[kj],df1.LAT[kj],'bo')
       thismanager = plt.get_current_fig_manager()
       thismanager.window.setGeometry(50,100,640, 545)  
       plt.show()
       print('before and after length of pts')
       print('before delete len='+str(len(df1)))
       for i in sorted(badplotpts)[::-1]:
         plt.plot(df1.LON[i],df1.LAT[i],'mo')
       print('after delete len='+str(len(lon)))
       df1.drop(badplotpts,inplace=True)
       plt.plot(df1.LON[i],df1.LAT[i],'co-')
       thismanager = plt.get_current_fig_manager()
       thismanager.window.setGeometry(50,100,640, 545) 
       plt.show()
       input(str(len(badplotpts))+' deleted from manual click on track. Press return to continue')  
     if k!=len(ids)-1:        
        raw_input("\n Press Enter to process next drifter")
  else:
     print(str(ids[k])+' is already loaded in ORACLE' ) 
fido.close()
fid.close()
fidids.close()
df1.drop(['MTH','DAY', 'HR_GMT', 'MIN', 'YEARDAY','temps'],inplace=True)
df1.to_csv(outdir+'prep_for_oracle_'+fn)
