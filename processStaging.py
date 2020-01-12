import json
import shutil as su
import hashlib
import os

def confirmfolder(targetdirectory):
    
    base=['storage']
    base.extend(targetdirectory)
    targetdirectory=base
    startingwd=os.getcwd()
    for folder in targetdirectory:
        if os.path.isdir(folder):
            os.chdir(folder)
        else:
            os.mkdir(folder)
            os.chdir(folder)
    
    os.chdir(startingwd)
   

def correctserverpath(fullpath):

    return 'storage'+fullpath



def gethash(filename):
    sha256_hash = hashlib.sha256()
 
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

with open('/home/pi/ftpsync/.client01Control/transferManifest.json') as infile:
	transferManifest=json.load(infile)
#print(transferManifest)
	
for idx, filehash in enumerate(transferManifest['transfer']):
    if transferManifest['transfer'][filehash]['transferred']==True and transferManifest['transfer'][filehash]['Processed']==False and gethash('.client01Staging/'+filehash)==filehash:
        paths=transferManifest['transfer'][filehash]['path']
        for path in paths:
            print(path)
            confirmfolder(path.split('/')[:-1])
            su.copy('.client01Staging/'+filehash,correctserverpath(path))
        os.remove('.client01Staging/'+filehash)
	
