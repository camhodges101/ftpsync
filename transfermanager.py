import socket, select
import json
import hashlib
from time import sleep
def gethash(filename):
    sha256_hash = hashlib.sha256()

    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def markack(filehash):
    
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

    result = select.select([s],[],[])
    msg = result[0][0].recv(bufferSize)
    msg=msg.decode('UTF-8')
    header,client,filehash=msg.split(',')
    markack(filehash)    
    print(msg)

