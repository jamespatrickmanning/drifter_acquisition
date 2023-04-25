#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 18:31:33 2023

@author: user
"""
def read_codes_names(id0):
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="codes.dat"
  #path1="/net/data5/jmanning/drift/"
  path1=""
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
        #print(name,lab,depth)
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

