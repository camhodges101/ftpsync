
const electron = require('electron');
const path = require('path');


const {app, BrowserWindow,ipcMain, ipcRenderer} = electron;

let mainWindow;
app.whenReady().then(() => {
  createWindow()
  console.log("creating main window")
  app.on('activate', function () {

    if (BrowserWindow.getAllWindows().length === 0) createWindow()

  })
})
function createWindow () {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 400,
    height: 800,
    resizable: false,
    frame: false,
    backgroundColor: '#2e2c29',
    webPreferences: {nodeIntegration: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // and load the index.html of the app.
  mainWindow.loadFile('index.html')

 
}

const mainMenuTemplate = [
  {
      label:"File",
      submenu:[


          {
              label:'Quit',
              accelerator: process.platform == 'darwin' ? 'Command+Q' : 
              'Ctrl+Q',
              click(){
                app.quit();  
              }
          }

      ]
  }
];

app.on('window-all-closed', function () {

  if (process.platform !== 'darwin') app.quit()
});



