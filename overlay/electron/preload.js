const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {

  analyzeText: (text) => ipcRenderer.invoke('analyze-text', text),
  
  // Hide overlay
  hideOverlay: () => ipcRenderer.send('hide-overlay'),
  
  // Show main window
  showMainWindow: () => ipcRenderer.send('show-main-window'),
  
  // Listen for text to analyze
  onAnalyzeText: (callback) => {
    ipcRenderer.on('analyze-text', (event, text) => callback(text));
  }
});
