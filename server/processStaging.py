import json
import shutil as su
import hashlib
from time import sleep
import os
serverUser = "pi"
'''
This script in required to take transferred files from the client staging folder and process them to the final back up folder


This script runs in the background on the raspberry pi server and waits for the send complete flag to be set to 1

Once this occurs the script sets the ready to receive flag to 0 to ensure the client doesn't send through any more files while its running

Next it runs through the Transfer manifest and looks for files that are marked is Tranferred = True, indicated they have already been check with their hash to ensure they are correctly transferred

These files are copied into their destination folders (these are created if no already existing)

As each file is moved it is marked as Processed = True in the transferManifest

Finally any files marked for deletion are moved to their archive directorys

At the end of the script all processed files are removed from the transferManifest

Finally the readyRecieve flag is set to 1 to allow the client to send new files. 
'''

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
    A key point here is to store the clients last modified time in the server manifest and not the last modified time of the server copy, this ensures we always maintain the newest version. 
    
    --Inputs: Filehash or Filepath, transfer mode
    
    --Actions: Reads latest serverManifest and updates it with the file hash of last file confirmed processed or file path of file archived.
    
    --Outputs: None

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
    
    --Inputs: Filehash as String or FilePath as String, Mode for whether part of transfer of new files or archive of deleted files

    --Actions:
    
    --Outputs: None
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
    '''
    Small function needed to correct path to server storage folder, will get removed soon.
    
    --Inputs: Filepath as string

    --Actions:
    
    --Outputs: path to storage location as string
    '''
    return 'storage'+fullpath



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
    

def archivefiles(filepath):
    '''
    Function to move files into their archive directory if marked for deletion, archive directory is create if not already existing
    
    --Inputs: Filepath as string
    
    --Actions:
    
    --Outputs: None
    '''
    confirmfolder(filepath.split('/'),'archive')
    su.move('storage'+filepath,'archive'+filepath+"/"+filepath.split('/')[-1])

#############################################
os.chdir('/home/{}/ftpsync/'.format(serverUser))

def checkSC():
    '''
    Function to check if the client has finished sending files and marked the send complete flag as 1

    --Inputs: None
    
    --Actions:
    
    --Outputs: Bool
    '''
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