def getwplot(infile):
 from datetime import datetime as dt
 if str(infile)=='drift_X.dat':
   including=[3352986,1350310,1350318]
   caseid=[1,1,1]
   startyd=[dt(2022,11,13,21,0,0),dt(2022,12,2,12,30,0),dt(2022,12,2,12,0,0)]
   endyd=[dt(2030,8,26,18,10,0),dt(2022,12,26,15,10,0),dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_glerl_2022_1.dat':
   including=[1350645]
   caseid=[1]
   startyd=[dt(2022,3,16,12,40,0)]
   endyd=[dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_jml_2022_3.dat':
   including=[3351589,3342429,3351974,3353539,3351586,3350345]
   caseid=[2,2,2,2,2,2]
   startyd=[dt(2022,11,9,0,30,0),dt(2022,11,9,0,50,0),dt(2022,11,9,0,30,0),dt(2022,11,9,0,50,0),dt(2022,11,9,0,0,0),dt(2022,11,9,0,0,0)]
   endyd=[dt(2030,11,5,15,0,0),dt(2030,11,4,9,10,0),dt(2030,8,26,18,10,0),dt(2030,8,26,18,10,0),dt(2030,11,4,23,10,0),dt(2030,11,4,13,0,0)]
 if str(infile)=='drift_jml_2022_2.dat':
   including=[3351589,3342429,3351974,3353539,3351586,3350345]
   caseid=[1,1,1,1,1,1]
   startyd=[dt(2022,11,2,0,30,0),dt(2022,11,2,0,50,0),dt(2022,11,2,0,30,0),dt(2022,11,2,0,50,0),dt(2022,11,2,0,0,0),dt(2022,11,2,0,0,0)]
   endyd=[dt(2022,11,5,15,0,0),dt(2022,11,4,9,10,0),dt(2030,8,26,18,10,0),dt(2030,8,26,18,10,0),dt(2022,11,4,23,10,0),dt(2022,11,4,13,0,0)]
 if str(infile)=='drift_rlsa_2022_1.dat':
   including=[3350689]
   caseid=[1]
   startyd=[dt(2022,3,16,12,40,0)]
   endyd=[dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_wms_2022_1.dat':
  including=[3391588]
  caseid=[1]
  startyd=[dt(2022,2,9,1,0,0)]
  endyd=[dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_whs_2022_1.dat':
  including=[3352986]
  caseid=[1]
  startyd=[dt(2022,11,13,21,0,0)]
  endyd=[dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_mbs_2022_1.dat':
  including=[3352402,3353881]
  caseid=[1,1]
  startyd=[dt(2022,12,1,1,0,0),dt(2022,12,1,1,0,0)]
  endyd=[dt(2030,8,26,18,10,0),dt(2030,8,26,18,10,0)]
 if str(infile)=='drift_fhs_2022_1.dat':
  including=[1367839,1350310,1350318,1374026]
  caseid=[1,1,1,1]
  startyd=[dt(2022,12,10,1,0,0),dt(2022,12,2,12,30,0),dt(2022,12,2,12,0,0),dt(2022,12,10,1,0,0)]
  endyd=[dt(2030,8,26,18,10,0),dt(2022,12,26,15,10,0),dt(2030,8,26,18,10,0),dt(2030,8,26,18,10,0)]
 return including,caseid,startyd,endyd
def read_codes():
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="codes.dat"
  #path1="/net/data5/jmanning/drift/"
  path1='/home/user/drift/'
  f1=open(path1+inputfile1,'r')
  esn,id,depth,lab,name=[],[],[],[],[]
  for line in f1:
    #print line
    esn.append(line.split()[0])
    id.append(line.split()[1])
    depth.append(line.split()[2]) 
    #if depth[-1]<=0.1:
    #  lab.append(line.split()[3])
    #  name.append(line.split()[4])
    #else:
    # lab.append('')
    #  name.append('')
  #return esn, id,depth,lab,name
  return esn, id,depth
