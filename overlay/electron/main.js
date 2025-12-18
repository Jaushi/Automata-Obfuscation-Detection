const { app, BrowserWindow, globalShortcut, ipcMain, screen, clipboard } = require('electron');
const path = require('path');

let mainWindow = null;
let overlayWindow = null;
let isOverlayVisible = false;

// Create hidden main window (runs in background)
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    show: false, 
    frame: false,
    transparent: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load your React app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

// Create overlay window 
function createOverlayWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  
  overlayWindow = new BrowserWindow({
    width: 500,
    height: 400,
    x: Math.floor((width - 500) / 2), 
    y: Math.floor(height * 0.3), 
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load overlay UI
  if (process.env.NODE_ENV === 'development') {
    overlayWindow.loadURL('http://localhost:5173/#/overlay');
  } else {
    overlayWindow.loadFile(path.join(__dirname, '../dist/index.html'), {
      hash: 'overlay'
    });
  }

  overlayWindow.on('blur', () => {
    // Auto-hide when clicking outside 
    hideOverlay();
  });
}

// Toggle overlay visibility
function toggleOverlay() {
  if (!overlayWindow) {
    createOverlayWindow();
  }

  if (isOverlayVisible) {
    hideOverlay();
  } else {
    showOverlay();
  }
}

function showOverlay() {
  if (overlayWindow) {
    // Get selected text or clipboard content
    const selectedText = clipboard.readText();
    
    // Send text to overlay for analysis
    overlayWindow.webContents.send('analyze-text', selectedText);
    
    overlayWindow.show();
    overlayWindow.focus();
    isOverlayVisible = true;
  }
}

function hideOverlay() {
  if (overlayWindow) {
    overlayWindow.hide();
    isOverlayVisible = false;
  }
}

// App initialization
app.whenReady().then(() => {
  createMainWindow();
  createOverlayWindow();

  // Register global hotkey (Cmd+Shift+D or Ctrl+Shift+D)
  const hotkey = process.platform === 'darwin' ? 'Command+Shift+D' : 'Control+Shift+D';
  
  globalShortcut.register(hotkey, () => {
    toggleOverlay();
  });

  console.log(`Taglish Detector running. Press ${hotkey} to activate overlay.`);

  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});


ipcMain.handle('analyze-text', async (event, text) => {
 
  try {
    const response = await fetch('http://localhost:5000/api/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return { error: 'Failed to analyze text' };
  }
});

ipcMain.on('hide-overlay', () => {
  hideOverlay();
});

ipcMain.on('show-main-window', () => {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
