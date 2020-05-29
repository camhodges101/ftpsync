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

from datetime import datetime
'''
This is a simple import of settings specific to my network, sourcing from a JSON allows for easy updating and keeps them out of the a public repo
'''
with open(".sftpcreds.json") as infile:
    CredientialConfig=json.load(infile)

SHAREDIR=CredientialConfig["sharedir"]
CLIENTID=CredientialConfig["clientID"]
SERVERHOST=CredientialConfig["serverHost"]
PORT=CredientialConfig["port"]
SSHKEY=CredientialConfig["sshkey"]
SERVERUSER=CredientialConfig["serverUser"]


def gethash(filename):
        '''
        basic function to take a filepath and return the SHA256 hash for the file
        '''
        sha256_hash = hashlib.sha256()
    
        with open(filename,"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        
def writetologs(message):
    '''
    function to write strings with timestamp to a logfile for troubleshooting
    '''
    timestamp=datetime.now()
    file_object = open('sftpSync.log', 'a')
    file_object.write(str(timestamp)+" - "+message+"\n")
     
    file_object.close()
    

def senddata(msg):
    '''
    Function to send state update messages to the GUI, currently uses IP socket to localhost, to be replaced with UNIX Domain Socket
    '''
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5025
    MESSAGE = bytes(msg,'utf-8')
     
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

def generateTransferManifest(clientManifest,serverManifest):
    '''
    Function takes the most up-to-date client manifest and server manifest and compares them. Looks for files that aren't on the server or the server version is older, this files are added to a dict (under the top level key "Transfer") along with they critical properaties (SHA256 hash, last modified times, file directories)
    Duplicate files with the same hash only appear once in this dict, a unique key (the hash) can have multiple paths and last modified times, these are stored in lists under the key "hash" and "lastmodtime".
    Files on the that are no longer on the client are added to the dict under the top level key "delete". 
    The entire dict is then dumped to the server using the pysftp library
    '''
    with sftp.open("/home/{}/ftpsync/.client01Control/transferManifest.json".format(SERVERUSER)) as infile:
        try:
            transfermanifest = json.load(infile)
        except:
            transfermanifest = {"transfer":{},"delete":{}}
            writetologs("Existing Transfer Manifest Corrupt, starting fresh")
    writetologs("Creating Outdated Transfer Manifest")
    for file in clientManifest:
        if file not in serverManifest or clientManifest[file]['lastmodtime']>serverManifest[file]['lastmodtime']:

            filename=file
           
            filehash=gethash(SHAREDIR+file)
            lastmodifiedtime=clientManifest[file]['lastmodtime']
            if filehash not in transfermanifest['transfer']:
                transfermanifest['transfer'][filehash]={'path':[],'lastmodtime':[],'transferred':False,'Processed':False}
    
            transfermanifest['transfer'][filehash]['path']+=[filename]
            transfermanifest['transfer'][filehash]['lastmodtime']+=[lastmodifiedtime]
    
    
    for file in serverManifest:
        if file not in clientManifest:
            transfermanifest["delete"][file]={"hash":serverManifest[file]["hash"],"lastmodtime":serverManifest[file]["lastmodtime"],"Processed":False}
            writetologs("Deleting: {}".format(file))
    
    writetologs("Sending Transfer Manifest")    
    with sftp.open("/home/{}/ftpsync/.client01Control/transferManifest.json".format(SERVERUSER),'w') as outfile:
        json.dump(transfermanifest,outfile)
    
    return transfermanifest
def getServerManifest():
    writetologs("Got Server Manifest")
    with sftp.open("/home/{}/ftpsync/serverManifest.json".format(SERVERUSER)) as infile:
        serverManifest = json.load(infile)
    return serverManifest
def checkR2R():
    flagFile=sftp.open("/home/{}/ftpsync/.client01Control/readyReceive".format(SERVERUSER), "r")
    return int(flagFile.read())==1
def sendfile(localpath,remotepath):
    sftp.put(localpath,remotepath)
def sendCompletebit(value):
    text_file = sftp.open("/home/{}/ftpsync/.client01Control/sendComplete".format(SERVERUSER), "w")
    n = text_file.write(str(value))
    text_file.close()
def sendack(filehash):
    UDP_IP = SERVERHOST
    UDP_PORT = 5005
    client=CLIENTID
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
    writetologs("Updating Client Manifest")
    listing=os.walk(SHAREDIR)
    for items in listing:
        parent_directory, subdirectory, files=items[0],items[1],items[2]
        
        
        for file in files:
            filepath=parent_directory+'/'+file
            manifest[filepath[len(SHAREDIR):]]={'hash':'','lastmodtime':0,'flags':[0,0,0],'repeat':False}
            ##Flag format delete,transfer,other
    
    
    
    
    
    def gethash(filename):
        sha256_hash = hashlib.sha256()
    
        with open(filename,"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        
    for idx, file in enumerate(manifest):
        #manifest[file]['hash']=gethash(sharedir+file)
        manifest[file]['lastmodtime']=os.path.getmtime(SHAREDIR+file)

    return manifest
while True:
    
    try:    
        while True:
            try:    
                check_output(['ping','-c','1',SERVERHOST],timeout=0.25)
                writetologs("Connection Established")
                outdateManifest=updateManifest()
                break
            except:
                outdateManifest=updateManifest()
                writetologs("No Connection")
                #Send Disconnected Message to GUI
                senddata(",".join(["0x10",str(""),str(""),"",SERVERHOST,"Disconnected"]))
                time.sleep(120)
      
        count=1
        #cnopts = pysftp.CnOpts(knownhosts='/home/cameron/.ssh/known_hosts')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None   
        #cnopts.hostkeys.load('/home/cameron/.ssh/known_hosts')  
        with pysftp.Connection(host=SERVERHOST,username=SERVERUSER,port=PORT,private_key=SSHKEY,cnopts=cnopts) as sftp:
            #Send Connected Message to GUI
            #Send Transfer Mode Idle to GUI
            senddata(",".join(["0x10",str(""),str(""),"Idle",SERVERHOST,"Connected"]))
            while not checkR2R():
                time.sleep(5)
            
            serverManifest=getServerManifest()
        
            sendCompletebit(0) 
            senddata(",".join(["0x10",str(""),str(""),"Indexing",SERVERHOST,"Connected"]))
            #print('sent manifest')
            transferManifest=generateTransferManifest(outdateManifest,serverManifest)
            #Send transfer mode Transferring message to GUI
            #Send Number of files to transfer to GUI len(transferManifest)
            senddata(",".join(["0x10",str(""),str(""),"Idle",SERVERHOST,"Connected"]))
            if len(transferManifest['transfer'])>0 or len(transferManifest['delete'])>0:
                senddata(",".join(["0x10",str(len(transferManifest['transfer'])),str(""),"Idle",SERVERHOST,"Connected"]))
                for idx,filehash in enumerate(transferManifest['transfer']):
                    #Send number of files transfered update to GUI idx
                    senddata(",".join(["0x10",str(len(transferManifest['transfer'])),str(idx),"Transferring",SERVERHOST,"Connected"]))
                    print(filehash)
                    filename=transferManifest['transfer'][filehash]['path'][0]
            
                    if transferManifest['transfer'][filehash]['transferred']==False:
                        writetologs("Transferring {}".format(filename))
                        sendfile(SHAREDIR+'/'+filename,'/home/{}/ftpsync/.client01Staging/{}'.format(SERVERUSER,filehash))
                        sendack(filehash)
                        '''
                        If we send message too fast the Rasp pi can't process them, drops messages and therefore doesn't mark the files as confirmed transferred, added a delay to allow the Pi to catch up, this is super hacky, need to come up with a better method. 
                        '''
                        time.sleep(0.8) 
                        transferManifest['transfer'][filehash]['transferred']=True
            
                    print(count,'/',len(outdateManifest)) 
                    count+=1
                sendCompletebit(1) 
            sftp.close()
            senddata(",".join(["0x10",str(""),str(""),"Idle",SERVERUSER,"Connected"]))
        time.sleep(60)

    except:
        writetologs("Connection Lost, Retrying")
        time.sleep(120)
        pass


