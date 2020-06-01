import json
import shutil as su
import hashlib
from time import sleep
import os
serverUser = "pi"
def confirmtransfercomplete():
    '''
    Function runs through the transfer manifest and removed items that have been processed (either moved to the correct location or archived)
    '''
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
        transferManifest=json.load(infile)
    transdict=transferManifest.copy()
    for filehash in list(transferManifest['transfer']):
        if transferManifest['transfer'][filehash]['transferred']==True and transferManifest['transfer'][filehash]['Processed']==True:
            del transdict['transfer'][filehash]
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
            json.dump(transdict,outfile)
            
            
            
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
        transferManifest=json.load(infile)
    transdict=transferManifest.copy()
    for filepath in list(transferManifest['delete']):
        if transferManifest['delete'][filepath]['Processed']==True:
            del transdict['delete'][filepath]
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
            json.dump(transdict,outfile)

def readyRecievebit(value):
    '''
    Sets the readyRecieve flag on the server to 0 or 1 to indicate it's finished processing files and the client can send new files 
    '''
    text_file = open("/home/{}/ftpsync/.client01Control/readyReceive".format(serverUser), "w")
    n = text_file.write(str(value))
    text_file.close()        


def confirmfolder(targetdirectory, basepath="storage"):
    '''
    This checks if a files destination directory exists and if it doesn't then it creates it.
    '''
    if basepath == 'storage':
        base=['storage']
    else:
        base=['archive']
    base.extend(targetdirectory)
    targetdirectory=base
    targetdirectory=list(filter(None,targetdirectory))
    startingwd=os.getcwd()
    for folder in targetdirectory:
        if os.path.isdir(folder):
            os.chdir(folder)
        else:
            os.mkdir(folder)
            os.chdir(folder)

    os.chdir(startingwd)

def updateServerManifest(filepath='', filehash='',lastmodtime='',mode="Transfer"):
    '''
    This function updates the server manifest as files are processed.
    A key point here is to store the clients last modified time in the server manifest and no the last modified time of the server copy, this ensures we always maintain the newest version. 
    '''
    with open('/home/{}/ftpsync/serverManifest.json'.format(serverUser),'r') as infile:
        serverManifest=json.load(infile)
    
    if mode == "Transfer":
        serverManifest[filepath]={'hash':filehash,'lastmodtime':lastmodtime,'flags':[0,0,0],'repeat':False}
        with open('/home/{}/ftpsync/serverManifest.json'.format(serverUser),'w') as outfile:
            json.dump(serverManifest,outfile)
        
    elif mode == "archive":
        serverDict=serverManifest.copy()
        del serverDict[filepath]
        with open('/home/{}/ftpsync/serverManifest.json'.format(serverUser),'w') as outfile:
            json.dump(serverDict,outfile)



def updateTransferManifest(filehash='',filepath='',mode="transfer"):
    '''
    This updates the processed indicators in the transfer manifest as each file is processed (moved to correct directory or archived)
    This seems inefficient to open and save the json for every file. the idea is to write changes to disk as often as possible so work doesn't need to be repeated if the server loses power during processing.
    '''
    if mode == 'transfer':
        with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
            transferManifest=json.load(infile)
        transferManifest['transfer'][filehash]['Processed']=True
        with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
            json.dump(transferManifest,outfile)

    elif mode == "archive":
        with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
            transferManifest=json.load(infile)
        transferManifest['delete'][filepath]['Processed']=True
        with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
            json.dump(transferManifest,outfile) 
def  correctserverpath(fullpath):

    return 'storage'+fullpath



def gethash(filename):
    '''
    basic function to take a filepath and return the SHA256 hash for the file

    --Inputs: filepath as string

    --Outputs: filehash as string
    '''
    sha256_hash = hashlib.sha256()

    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    

def archivefiles(filepath):
    confirmfolder(filepath.split('/'),'archive')
    su.move('storage'+filepath,'archive'+filepath+"/"+filepath.split('/')[-1])

#############################################
os.chdir('/home/{}/ftpsync/'.format(serverUser))

def checkSC():
    flagFile=open("/home/{}/ftpsync/.client01Control/sendComplete".format(serverUser), "r")
    return int(flagFile.read())==1


while True:
    if checkSC():
        readyRecievebit(0)
        with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser)) as infile:
            transferManifest=json.load(infile)
        #print(transferManifest)
        
        for idx, filehash in enumerate(transferManifest['transfer']):
            '''
            This step checks if a file is confirmed as transferred, hasn't yet been process and that the files SHA256 hash matches the expected hash. If the file hash doesn't match the expected hash the file is ignored and will be overwritten on teh next sync attempt. 
            This is a critical step to ensure we don't back up a corrupted copy of a file. 
            
            '''
            if transferManifest['transfer'][filehash]['transferred']==True and transferManifest['transfer'][filehash]['Processed']==False and gethash('.client01Staging/'+filehash)==filehash:
                paths=transferManifest['transfer'][filehash]['path']
                modtimes=transferManifest['transfer'][filehash]['lastmodtime']
                print('{}-{}'.format(idx,filehash))
                for path,modtime in zip(paths,modtimes):
                    confirmfolder(path.split('/')[:-1])
                    su.copy('.client01Staging/'+filehash,correctserverpath(path))
                    updateServerManifest(path,filehash,modtime)
                updateTransferManifest(filehash)
                os.remove('.client01Staging/'+filehash)
        for idx, filepath in enumerate(transferManifest['delete']):
            archivefiles(filepath)
            updateTransferManifest(filepath=filepath,mode="archive")
            updateServerManifest(filepath=filepath,mode="archive")
            print("archiving files")
        confirmtransfercomplete()
        readyRecievebit(1)
    sleep(30)