def getwplot(infile):  
 from datetime import datetime as dt
 from matplotlib.dates import date2num,num2date
 yystart=2012
 yyend=2013
 if str(infile)=='drift_2013.dat' or str(infile)=='drift_X.dat':
   print 'this is all 2013'  
   including=[945770,948061,949876,949812,950084,1236780,
    327457,          
    947763,951965,326839,946974,
    319760,
    946956,
    331187,320231,322948,
    1235971]
   caseid=[1,1,1,1,1,1,
   1,
   1,1,1,1,
   1,
   1,
   1,1,1,
   1];
   startyd=[date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2013,2,13,13,0,0))-date2num(dt(2013,1,1,0,0)),
            date2num(dt(2012,12,7,17,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,10,24,12,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,10,20,22,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,12,1,13,35,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,12,1,13,11,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,12,1,12,40,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2013,2,12,20,0,0))-date2num(dt(2013,1,1,0,0))]
   endyd=[365.,365.,365.,365.,365.,365.,
    365.,
    365.,365.,365.,365.,
    365.,
    365.,
    365.,365.,365.,
    365.]
 if str(infile)=='drift_pifsc_2012_1.dat':
   including=[368945,323168,329268,320278]
   caseid=[1,1,1,1]
   startyd=[date2num(dt(2012,11,8,11,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,11,8,11,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,11,11,11,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,11,11,11,0,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,date2num(dt(2012,11,20,18,0,0))-date2num(dt(2012,1,1,0,0)),365.]
 if str(infile)=='drift_smcc_2013_1.dat':
   including=[1235971]
   caseid=[1]
   startyd=[date2num(dt(2013,2,13,0,0,0))-date2num(dt(2013,1,1,0,0))]
   endyd=[365.]
 if str(infile)=='drift_udel_2012_2.dat':
   including=[319760]
   caseid=[1]
   startyd=[date2num(dt(2012,10,24,12,30,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.]
 if str(infile)=='drift_ep_2012_2.dat':
   including=[331187,320231,322948]
   caseid=[1,1,1]
   startyd=[date2num(dt(2012,12,1,13,35,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,12,1,13,11,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,12,1,12,40,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,365.]   
 if str(infile)=='drift_turtle_2012_2.dat':
   including=[946956,945725,948887,950556]
   caseid=[1,1,1,1]
   startyd=[date2num(dt(2012,10,20,22,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,10,20,22,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,10,23,22,0,0))-date2num(dt(2012,1,1,0,0)),date2num(dt(2012,10,20,22,0,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,365.,365.]   

   
 if str(infile)=='drift_udel_2012_1.dat':
   including=[368790,319760]
   caseid=[1,1]
   startyd=[date2num(dt(2012,8,21,0,30,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,10,24,12,0,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.]

 if str(infile)=='drift_turtle_2012_1.dat':
   including=[947601,947499,322964,946254]
   caseid=[1,1,1,1]
   startyd=[date2num(dt(2012,7,18,14,15,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,7,18,14,15,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,7,18,13,29,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,7,18,13,29,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,365.,365.]


 if str(infile)=='drift_tas_2012_1.dat':
   including=[947763,951965,326839,946974]
   caseid=[1,1,1,1]
   startyd=[date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,6,1,3,0,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,365.,365.]

 if str(infile)=='drift_psu_2012_1.dat':
   including=[947623,949929,950842,950842,321808,327457]
   caseid=[1,1,1,2,1,1]
   startyd=[date2num(dt(2012,5,7,14,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,7,15,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,17,15,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,9,25,15,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,11,9,23,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,12,7,17,0,0))-date2num(dt(2012,1,1,0,0))]
   endyd=[365.,365.,date2num(dt(2012,6,30,15,0,0))-date2num(dt(2012,1,1,0,0)),365.,365.,365.]

 if str(infile)=='drift_ep_2012_1.dat':
   including=[945770,948061,949876,949812,950084,1236780]
   caseid=[1,1,1,1,1,1]
   startyd=[date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2012,5,12,13,0,0))-date2num(dt(2012,1,1,0,0)),
            date2num(dt(2013,2,13,13,0,0))-date2num(dt(2013,1,1,0,0))]
   endyd=[365.,365.,365.,365.,365.,365.]

 #put start and stop date in datetime format 
 start_datet,end_datet=[],[]
 for k in range(len(startyd)):
     if (type(startyd[k])<>dt):  
       if (including[k]==1235971) or (including[k]==1236780):
           yystart=2013
       else:
           yystart=2012
       start_datet.append(num2date(startyd[k]+1.).replace(year=yystart).replace(tzinfo=None))
       end_datet.append(num2date(endyd[k]).replace(year=yyend).replace(tzinfo=None))
     else:
       start_datet.append(startyd[k]) 
       end_datet.append(endyd[k])
 return including,caseid,start_datet,end_datet


def read_codes():
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="codes.dat"
  path1="/net/data5/jmanning/drift/"
  f1=open(path1+inputfile1,'r')
  esn,id,depth=[],[],[]
  for line in f1:
    esn.append(line.split()[0])
    id.append(line.split()[1])
    depth.append(line.split()[2])
  return esn, id,depth
