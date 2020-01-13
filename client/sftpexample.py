#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 15:36:37 2019

@author: cameron
"""
import os
import pysftp
import time
import json
import socket
import hashlib
from subprocess import check_output

#%%

sharedir='/home/cameron/ftpsync'
clientID='01'
serverHost='192.168.0.125'
port=55
sshkey='~/.ssh/testpi.key'
serverUser='cameron'


def generateTransferManifest(clientManifest,serverManifest):

    with sftp.open("/home/cameron/ftpsync/.client01Control/transferManifest.json") as infile:
        transfermanifest = json.load(infile)
    for file in clientManifest:
        if file not in serverManifest or clientManifest[file]['lastmodtime']>serverManifest[file]['lastmodtime']:
            print(file)
            filename=file
            filehash=clientManifest[file]['hash']
            lastmodifiedtime=clientManifest[file]['modtime']
            if filehash not in transfermanifest['transfer']:
                transfermanifest['transfer'][filehash]={'path':[],'lastmodtime':0,'transferred':False,'Processed':False}
    
            transfermanifest['transfer'][filehash]['path']+=[filename]
            transfermanifest['transfer'][filehash]['lastmodtime']=lastmodifiedtime
        
    with sftp.open("/home/cameron/ftpsync/.client01Control/transferManifest.json",'w') as outfile:
        json.dump(transfermanifest,outfile)
    
    return transfermanifest


def getServerManifest():
    with sftp.open("/home/cameron/ftpsync/serverManifest.json") as infile:
        serverManifest = json.load(infile)
    return serverManifest
def checkR2R():
    flagFile=sftp.open("/home/cameron/ftpsync/.client01Control/readyReceive", "r")
    return int(flagFile.read())==1


def sendfile(localpath,remotepath):
    sftp.put(localpath,remotepath)

def sendCompletebit(value):
    text_file = sftp.open("/home/cameron/ftpsync/.client01Control/sendComplete", "w")
    n = text_file.write(str(value))
    text_file.close()
def sendack(filehash):
    UDP_IP = serverHost
    UDP_PORT = 5005
    client=clientID
    message=bytes(str('transferacknowledge,'+client+','+filehash),'utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (UDP_IP, UDP_PORT))


def updateManifest():
    manifest={}
    listing=os.walk(sharedir)
    for items in listing:
        parent_directory, subdirectory, files=items[0],items[1],items[2]
        subdir=len(subdirectory)>0
        #subdir=False
        for file in files:
            filepath=parent_directory+'/'+file
            manifest[filepath[len(sharedir):]]={'hash':'','modtime':0,'flags':[0,0,0],'repeat':False}
            ##Flag format delete,transfer,other
    
    
    
    
    #filename = input("Enter the input file name: ")
    def gethash(filename):
        sha256_hash = hashlib.sha256()
    
        with open(filename,"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        
    for idx, file in enumerate(manifest):
        manifest[file]['hash']=gethash(sharedir+file)
        manifest[file]['modtime']=os.path.getmtime(sharedir+file)

    #with open('syncManifest.json','w') as outfile:
    #    json.dump(manifest,outfile)
    return manifest
while True:
    try:    
        check_output(['ping','-c','1',serverHost],timeout=0.25)
        outdateManifest=updateManifest()
        break
    except:
        outdateManifest=updateManifest()
        print("No Connection")

#def sendnewfiles(outdateManifest):
count=1
cnopts = pysftp.CnOpts()
cnopts.hostkeys.load('/home/cameron/.ssh/known_hosts')  
with pysftp.Connection(host=serverHost,username=serverUser,port=port,private_key=sshkey,cnopts=cnopts) as sftp:
    while not checkR2R():
        time.sleep(5)
    
    serverManifest=getServerManifest()
    

    
    sendCompletebit(0) 

    print('sent manifest')
    transferManifest=generateTransferManifest(outdateManifest,serverManifest)
    #print(transferManifest)
    
    
    for idx,filehash in enumerate(transferManifest['transfer']):
        
        print(filehash)
        filename=transferManifest['transfer'][filehash]['path'][0]
        #filehash=outdateManifest[file]['hash']
        
            
        
        if transferManifest['transfer'][filehash]['transferred']==False:
            
            sendfile(sharedir+'/'+filename,'/home/cameron/ftpsync/.client01Staging/'+filehash)
            sendack(filehash)
            transferManifest['transfer'][filehash]['transferred']=True
        
        
        
        print(count,'/',len(outdateManifest)) 
        count+=1
    sendCompletebit(1) 
    sftp.close()



