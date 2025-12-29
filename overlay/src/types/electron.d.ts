// Global type definitions for Electron API
interface ElectronAPI {
  analyzeText: (text: string) => Promise<any>;
  hideOverlay: () => void;
  showMainWindow: () => void;
  onAnalyzeText: (callback: (text: string) => void) => void;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
