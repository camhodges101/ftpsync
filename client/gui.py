  
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 20:04:25 2020

@author: hodgec
"""

import npyscreen
from datetime import datetime
import random
import socket
recentfilesdata=[['Filename','Last Modified Time', 'Size']]

latestserverattempt="Disconnected"
hostname='0.0.0.0'
transferMode='Idle'
nbfilessent=0
totalfiles=0

def getmessage(): 
    '''
    This function listens for state update messages from the client process, when received they are decoded and returned to the GUI process. 
    
    --Inputs: None
    
    --Actions: None
    
    --Outputs: Message data as a comma separated string.
    '''

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5025

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    return data.decode('utf-8')


class MyGrid(npyscreen.GridColTitles):
	pass

		   



class statusForm(npyscreen.Form):



    def while_waiting(self):
        '''
        The while_waiting method allows for a refresh of the displayed values when a message is recieved from the client process. 
        
        The message is a string with comma separate values. 
        
        We first read the values off the message which is identified by starting with "0x10"
        
        We then update the values below. 
        '''
        
        data=getmessage()
        if data.split(",")[0]=="0x10":
            self.nbFilesTotransfer=data.split(",")[2]
            self.totalNumberofFiles=data.split(",")[1]
            self.transferMode=data.split(",")[3]
            self.hostName=data.split(",")[4]
            self.connectionstate=data.split(",")[5]
       


        self.time.value=str(datetime.now())[:-7]
        self.filecount.value=(str(self.nbFilesTotransfer)+"/"+str(self.totalNumberofFiles))
        self.mode.value=self.transferMode
        self.host.value=self.hostName
        self.hoststatus.value=self.connectionstate
        self.gd.values = recentfilesdata
        self.display()
		
    def create(self):
        '''
        This creates the form outline showing the current state of the sftpsync process
        
        It also includes initial values which are later updated with data from the client process. 
        '''
        self.nbFilesTotransfer=nbfilessent
        self.transferMode=transferMode #Idle, Indexing, Transferring
        self.hostName=hostname
        self.totalNumberofFiles=totalfiles
        self.connectionstate=latestserverattempt #Connected, Connecting, Disconnected, 
        self.recentfileslist=recentfilesdata
        SPACING=35
        self.time  = self.add(npyscreen.TitleText, name = str("System Time:"),value='',editable=False,begin_entry_at=SPACING)
        self.filecount  = self.add(npyscreen.TitleText, name = str("Number of Files to Transfer:"),value='',editable=False,begin_entry_at=SPACING)
        self.mode  = self.add(npyscreen.TitleText, name = str("Transfer Mode: "),value='',editable=False,begin_entry_at=SPACING)
        self.host  = self.add(npyscreen.TitleText, name = str("Server Host Name: "),value='',editable=False,begin_entry_at=SPACING)
        self.hoststatus  = self.add(npyscreen.TitleText, name = str("Connection Status: "),value='',editable=False,begin_entry_at=SPACING)
        self.transferpause= self.add(npyscreen.TitleSelectOne, max_height =4, value = [0,], name="Pause sFTP Sync",
			values = ["Resume","Pause"], scroll_exit=True)

	
        self.gd = self.add(MyGrid)

        self.gd.values = recentfilesdata

        self.edit()
    
class sftpApp(npyscreen.NPSAppManaged):

	keypress_timeout_default = 5

	def onStart(self):
		self.addForm("MAIN", statusForm, name="sFTPSync")
		

if __name__ == '__main__':
    app = sftpApp()
    app.run()

