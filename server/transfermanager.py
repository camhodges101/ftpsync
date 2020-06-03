import socket, select
import json
import hashlib

import time

'''
This script runs on a constant loop, it is required to listen for UDP messages from client machine

Messages received contain client ID and file hash. 

When each hash is receieve it is check against the file to ensure it was transfer correctly and then marked in the transferManifest as transferred=True

This allows the client to restart where it left off if either the client or server process is restarted and ensures no corrupted files are backed up.
'''


def gethash(filename):
    '''
    basic function to take a filepath and return the SHA256 hash for the file

    --Inputs: filepath as string
    
    --Actions:
    
    --Outputs: filehash as string
    '''
    sha256_hash = hashlib.sha256()

    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def markack(filehash):
    '''
    Files are transferred with the SHA256 hash as it's file name, this file name can be checked against both the hash sent by the client and the actual calculated hash of the file recieved.
    
    --Inputs: Filehash as string

    --Actions: Loads latest transferManifest and marks filehash as Processed=True and resaves manifest. 
    
    --Outputs: None
    '''
    if gethash('ftpsync/.client01Staging/'+filehash)==filehash:
        with open('ftpsync/.client01Control/transferManifest.json') as infile:
            transfermanifest = json.load(infile)
        transfermanifest['transfer'][filehash]['transferred']=True

        with open('ftpsync/.client01Control/transferManifest.json','w') as json_file:
            json.dump(transfermanifest, json_file)


port = 5005
bufferSize=1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('',port))

while True:
    ti = time.time()
    result = select.select([s],[],[])
    msg = result[0][0].recv(bufferSize)
    msg=msg.decode('UTF-8')
    header,client,filehash=msg.split(',')
    markack(filehash)    
    print("{} -{}".format(round(time.time(),3)-ti,msg))

