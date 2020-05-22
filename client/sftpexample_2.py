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

sharedir='/home/cameron/Dropbox/CamsDocuments/ftpsync'
clientID='01'
serverHost='192.168.0.125'
port=55
sshkey='~/.ssh/testpi.key'
serverUser='pi'

def senddata(msg):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5025
    MESSAGE = bytes(msg,'utf-8')
     
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

def generateTransferManifest(clientManifest,serverManifest):

    with sftp.open("/home/{}/ftpsync/.client01Control/transferManifest.json".format(serverUser)) as infile:
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
        
    with sftp.open("/home/{}/ftpsync/.client01Control/transferManifest.json".format(serverUser),'w') as outfile:
        json.dump(transfermanifest,outfile)
    
    return transfermanifest
def getServerManifest():
    with sftp.open("/home/{}/ftpsync/serverManifest.json".format(serverUser)) as infile:
        serverManifest = json.load(infile)
    return serverManifest
def checkR2R():
    flagFile=sftp.open("/home/{}/ftpsync/.client01Control/readyReceive".format(serverUser), "r")
    return int(flagFile.read())==1
def sendfile(localpath,remotepath):
    sftp.put(localpath,remotepath)
def sendCompletebit(value):
    text_file = sftp.open("/home/{}/ftpsync/.client01Control/sendComplete".format(serverUser), "w")
    n = text_file.write(str(value))
    text_file.close()
def sendack(filehash):
    UDP_IP = serverHost
    UDP_PORT = 5005
    client=clientID
    message=bytes(str('transferacknowledge,'+client+','+filehash),'utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (UDP_IP, UDP_PORT))


'''
Message structure
<MessageID> 0x10
<Total Number of Files to Transfer> len(transferManifest)
<Files Remaining>
<Transfer Mode> transfermode
<Host Name> serverHost
<Connection State> lastserverattempt
''' 
    
    
def updateManifest():
    manifest={}
    listing=os.walk(sharedir)
    for items in listing:
        parent_directory, subdirectory, files=items[0],items[1],items[2]
        
        
        for file in files:
            filepath=parent_directory+'/'+file
            manifest[filepath[len(sharedir):]]={'hash':'','modtime':0,'flags':[0,0,0],'repeat':False}
            ##Flag format delete,transfer,other
    
    
    
    
    
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

    return manifest
while True:
    try:    
        check_output(['ping','-c','1',serverHost],timeout=0.25)
        outdateManifest=updateManifest()
        break
    except:
        outdateManifest=updateManifest()
        print("No Connection")
        #Send Disconnected Message to GUI
        senddata(",".join(["0x10",str(""),str(""),"",serverHost,"Disconnected"]))

count=1
cnopts = pysftp.CnOpts()
cnopts.hostkeys.load('/home/cameron/.ssh/known_hosts')  
with pysftp.Connection(host=serverHost,username=serverUser,port=port,private_key=sshkey,cnopts=cnopts) as sftp:
    #Send Connected Message to GUI
    #Send Transfer Mode Idle to GUI
    senddata(",".join(["0x10",str(""),str(""),"Idle",serverHost,"Connected"]))
    while not checkR2R():
        time.sleep(5)
    
    serverManifest=getServerManifest()

    sendCompletebit(0) 

    print('sent manifest')
    transferManifest=generateTransferManifest(outdateManifest,serverManifest)
    #Send transfer mode Transferring message to GUI
    #Send Number of files to transfer to GUI len(transferManifest)
    senddata(",".join(["0x10",str(len(transferManifest)),str(""),"Idle",serverHost,"Connected"]))
    for idx,filehash in enumerate(transferManifest['transfer']):
        #Send number of files transfered update to GUI idx
        senddata(",".join(["0x10",str(len(transferManifest)),str(idx),"Transferring",serverHost,"Connected"]))
        print(filehash)
        filename=transferManifest['transfer'][filehash]['path'][0]

        if transferManifest['transfer'][filehash]['transferred']==False:
            
            sendfile(sharedir+'/'+filename,'/home/{}/ftpsync/.client01Staging/{}'.format(serverName,filehash))
            sendack(filehash)
            transferManifest['transfer'][filehash]['transferred']=True

        print(count,'/',len(outdateManifest)) 
        count+=1
    sendCompletebit(1) 
    sftp.close()




