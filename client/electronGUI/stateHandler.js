const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const socket = require('socket.io')




function pauseSync(){
  var PRButton = document.getElementById("PauseButton")
  console.log("button pressed");
  if (PRButton.innerHTML == "Pause Sync"){
    PRButton.innerHTML = "Resume Sync";
  } else if (PRButton.innerHTML == "Resume Sync"){
    PRButton.innerHTML = "Pause Sync";
  };
};

server.on('error', (err) => {
  console.log(`server error:\n${err.stack}`);
  server.close();
});

server.on('message', (msg, rinfo) => {
  
  const msgstring = msg.toString();
  const msgID = msgstring.split(",")[0];
  if (msgID == "0x10"){
    const fileProgress = msgstring.split(",")[1];
    const totalFiles = msgstring.split(",")[2];
    const transferMode = msgstring.split(",")[3];
    const serverHost = msgstring.split(",")[4];
    const connectionState = msgstring.split(",")[5];
    var FILEPROGRESS = document.getElementById("transferfileCount");
    
    var TRANSFERMODE = document.getElementById("transferState");
    var SERVERHOST = document.getElementById("Hostname");
    var CONNECTIONSTATE = document.getElementById("connnect-state");
    if (transferMode != "Transferring") {
      FILEPROGRESS.textContent = `Waiting to start transfer`;
    } else {
        FILEPROGRESS.textContent = `Progress: ${fileProgress} / ${totalFiles}`;
      };
    
    TRANSFERMODE.textContent = `Transfer Mode:  ${transferMode}`;
    SERVERHOST.textContent = `Server Host:  ${serverHost}`;
    CONNECTIONSTATE.textContent = `Connection State:  ${connectionState}`;  
  }
  if (msgID == "0x20"){
    const fileliststring = msgstring.split(",")[1];
    const fileList = fileliststring.split(";").join("<br />");
    var UnsynedFiles = document.getElementById("Unsyncedfiles");
    UnsynedFiles.innerHTML = fileList;
  }
});

server.on('listening', () => {
  const address = server.address();
  console.log(`server listening ${address.address}:${address.port}`);
});

server.bind(3001);
var PRButton = document.getElementById("PauseButton")
PRButton.addEventListener('click', () => {
  
  pauseSync();

})