
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

latestserverattempt="Connected"
hostname='192.168.0.113'
transferMode='Idle'
nbfilessent=54
totalfiles=540

def getmessage(): 
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5025

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    return data.decode('utf-8')


class MyGrid(npyscreen.GridColTitles):
	pass
    # You need to override custom_print_cell to manipulate how
    # a cell is printed. In this example we change the color of the
    # text depending on the string value of cell.
    # def custom_print_cell(self, actual_cell, cell_display_value):
        # if cell_display_value =='FAIL':
           # actual_cell.color = 'DANGER'
        # elif cell_display_value == 'PASS':
           # actual_cell.color = 'GOOD'
        # else:
           # actual_cell.color = 'DEFAULT'
		   



class statusForm(npyscreen.Form):

#    def while_waiting(self):
        #npyscreen.notify_wait("Update")
        #self.date_widget.value = datetime.now()
        #self.display()

	def while_waiting(self):
        data=getmessage()
        if data.split(",")[0]=="0x10"
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
		self.nbFilesTotransfer=nbfilessent
		self.transferMode=transferMode #Idle, Indexing, Transferring
		self.hostName=hostname
		self.totalNumberofFiles=totalfiles
		self.connectionstate=latestserverattempt #Connected, Connecting, Disconnected, 
		self.recentfileslist=recentfilesdata
		spaceing=35
		self.time  = self.add(npyscreen.TitleText, name = str("Systtem Time:"),value='',editable=False,begin_entry_at=spaceing)
		self.filecount  = self.add(npyscreen.TitleText, name = str("Number of Files to Transfer:"),value='',editable=False,begin_entry_at=spaceing)
		self.mode  = self.add(npyscreen.TitleText, name = str("Transfer Mode: "),value='',editable=False,begin_entry_at=spaceing)
		self.host  = self.add(npyscreen.TitleText, name = str("Server Host Name: "),value='',editable=False,begin_entry_at=spaceing)
		self.hoststatus  = self.add(npyscreen.TitleText, name = str("Connection Status: "),value='',editable=False,begin_entry_at=spaceing)
		self.transferpause= self.add(npyscreen.TitleSelectOne, max_height =4, value = [0,], name="Pause sFTP Sync",
			values = ["Resume","Pause"], scroll_exit=True)

	
		self.gd = self.add(MyGrid)

				# Adding values to the Grid, this code just randomly
				# fills a 2 x 4 grid with random PASS/FAIL strings.
		self.gd.values = recentfilesdata

		self.edit()
#	def create(self):
#        self.date_widget = self.add(npyscreen.FixedText,value=datetime.now(), editable=False)
    
class sftpApp(npyscreen.NPSAppManaged):

	keypress_timeout_default = 5

	def onStart(self):
		self.addForm("MAIN", statusForm, name="sFTPSync")
		

if __name__ == '__main__':
    app = sftpApp()
    app.run()

