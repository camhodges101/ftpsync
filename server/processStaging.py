import json
import shutil as su
import hashlib
from time import sleep
import os
serverUser = "pi"
def confirmtransfercomplete():
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
        transferManifest=json.load(infile)
    transdict=transferManifest.copy()
    for filehash in list(transferManifest['transfer']):
        if transferManifest['transfer'][filehash]['transferred']==True and transferManifest['transfer'][filehash]['Processed']==True:
            del transdict['transfer'][filehash]
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
            json.dump(transdict,outfile)

def readyRecievebit(value):
    text_file = open("/home/{}/ftpsync/.client01Control/readyReceive".format(serverUser), "w")
    n = text_file.write(str(value))
    text_file.close()        


def confirmfolder(targetdirectory, basepath="storage"):
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

def updateServerManifest(filepath, filehash,lastmodtime):
    with open('/home/{}/ftpsync/serverManifest.json'.format(serverUser),'r') as infile:
        serverManifest=json.load(infile)
    serverManifest[filepath]={'hash':filehash,'lastmodtime':lastmodtime,'flags':[0,0,0],'repeat':False}
    with open('/home/{}/ftpsync/serverManifest.json'.format(serverUser),'w') as outfile:
        json.dump(serverManifest,outfile)

def updateTransferManifest(filehash):
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'r') as infile:
        transferManifest=json.load(infile)
    transferManifest['transfer'][filehash]['Processed']=True
    with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser),'w') as outfile:
        json.dump(transferManifest,outfile)


def  correctserverpath(fullpath):

    return 'storage'+fullpath



def gethash(filename):
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
        confirmtransfercomplete()
        readyRecievebit(1)
    sleep(30)