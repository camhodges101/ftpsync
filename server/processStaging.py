import json
import shutil as su
import hashlib
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
        


def confirmfolder(targetdirectory):

    base=['storage']
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

os.chdir('/home/{}/ftpsync/'.format(serverUser))

with open('/home/{}/ftpsync/.client01Control/transferManifest.json'.format(serverUser)) as infile:
    transferManifest=json.load(infile)
#print(transferManifest)

for idx, filehash in enumerate(transferManifest['transfer']):
    if transferManifest['transfer'][filehash]['transferred']==True and transferManifest['transfer'][filehash]['Processed']==False and gethash('.client01Staging/'+filehash)==filehash:
        paths=transferManifest['transfer'][filehash]['path']
        print('{}-{}'.format(idx,filehash))
        for path in paths:
            confirmfolder(path.split('/')[:-1])
            su.copy('.client01Staging/'+filehash,correctserverpath(path))
        updateServerManifest(path,filehash,transferManifest['transfer'][filehash]['lastmodtime'])
        updateTransferManifest(filehash)
        os.remove('.client01Staging/'+filehash)

confirmtransfercomplete()
