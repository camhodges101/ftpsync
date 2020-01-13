#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 06:36:07 2019

@author: cameron
"""
import os
#%%
ftpshare={}

ftpshare['Documents']={}
ftpshare['Downloads']={}
ftpshare['Pictures']={}


#%%
ftpshare['Documents']['Job Application']={}
ftpshare['Documents']['Uniwork']={}
ftpshare['Pictures']['Holiday']={}
#%%
ftpshare['Pictures']['Holiday']['Trip1']={}
ftpshare['Pictures']['Holiday']['Trip2']={}
ftpshare['Pictures']['Holiday']['Trip3']={}

#%%

for idx,keys in enumerate(ftpshare):
    directory=keys
    #print(directory)
    for idx2,items in enumerate(ftpshare[directory]):
        print(len(ftpshare[keys]),',',directory,"-",items)
        
#%%
foldername='pictures'
command='mkdir '+foldername

os.system(command)

#%%
ftpshare=[['Documents','"Job Application"'],
['Documents','Uniwork'],
['Pictures','Holiday'],
['Pictures','Holiday','Trip1'],
['Pictures','Holiday','Trip2'],
['Pictures','Holiday','Trip3']]
treelength=0
for paths in ftpshare:
    treelength=max(treelength,len(paths))
        
        
        
def createpath(tree):
    outputstring=''
    for items in tree:
        outputstring=outputstring+items+'/'
    return outputstring[:-1]

for i in range(treelength):      
    for foldertree in ftpshare:
        try:
            path=createpath(foldertree[:i+1])
            command='mkdir '+path  
            os.system(command)
        except:
            print('blah')
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        