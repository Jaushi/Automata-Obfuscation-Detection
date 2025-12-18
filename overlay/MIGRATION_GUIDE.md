# Taglish Detector Overlay - Migration Guide

## 🎯 Overview

This overlay wrapper enables your Taglish Detector to work as a **system-wide overlay** similar to Siri/Spotlight, allowing real-time obfuscation detection across any application (Messenger, Discord, WhatsApp, etc.).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  OS Level (Windows/Mac/Linux)                   │
│  ┌───────────────────────────────────────────┐  │
│  │  Global Hotkey: Ctrl+Shift+D              │  │
│  │  Clipboard Monitor                        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────▼────────┐
         │  Electron Main  │
         │  Process        │
         └────────┬────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
┌────▼─────┐          ┌───────▼────────┐
│ Overlay  │          │  Main Window   │
│ Window   │          │  (Hidden/Tray) │
│ (Popup)  │          │                │
└────┬─────┘          └────────────────┘
     │
     │  Your existing React App
     │  (runs in both contexts)
     │
┌────▼─────────────────────┐
│  Flask Backend API       │
│  http://localhost:5000   │
└──────────────────────────┘
```

## 🚀 How It Works

1. **User selects text** in any app (Messenger, Discord, etc.)
2. **Presses `Ctrl+Shift+D`** (or `Cmd+Shift+D` on Mac)
3. **Overlay appears** as a floating window (Siri-style)
4. **Text is automatically analyzed** via your Flask API
5. **Results shown instantly** with deciphered text
6. **Click outside to dismiss** - seamless experience

## 📦 Migration Steps

### Step 1: Copy Your Client Code

```bash
# From project root
cp -r client/* overlay/
```

### Step 2: Install Overlay Dependencies

```bash
cd overlay
npm install
```

### Step 3: Update Your Routes

Add overlay route to `overlay/src/App.tsx`:

```typescript
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import OverlayView from './pages/OverlayView';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/overlay" element={<OverlayView />} />
      </Routes>
    </Router>
  );
}

export default App;
```

### Step 4: Run Development Mode

```bash
# Terminal 1: Start Flask backend (from server folder)
cd ../server
python run.py

# Terminal 2: Start Electron overlay (from overlay folder)
cd ../overlay
npm run dev
```

## ⌨️ Usage

### Development Mode
- Press `Ctrl+Shift+D` anywhere to activate overlay
- Select/copy text before activating for auto-analysis
- Press `ESC` or click outside to close

### Production Build
```bash
npm run build
npm run build:electron
```

This creates an installable app in `dist-electron/`

## 🎨 Features

### ✅ Implemented
- Global hotkey activation (`Ctrl+Shift+D`)
- Siri-style frosted glass overlay
- Auto-capture of selected/clipboard text
- Real-time analysis via Flask API
- Auto-hide on blur (click outside)
- System tray integration (background mode)

### 🔮 Future Enhancements
- **OCR Integration**: Read text directly from screen (no selection needed)
- **Auto-detection**: Monitor clipboard continuously
- **Multiple languages**: Support more language pairs
- **Custom hotkeys**: User-configurable shortcuts
- **History**: Keep track of analyzed texts
- **Tooltip mode**: Hover over text to analyze

## 🔧 Configuration

### Change Hotkey

Edit `overlay/electron/main.js`:

```javascript
// Change from Ctrl+Shift+D to your preference
const hotkey = 'Control+Alt+T'; // Windows/Linux
// or
const hotkey = 'Command+Option+T'; // macOS
```

### API Endpoint

Edit `overlay/electron/main.js`:

```javascript
// Change Flask API URL
const response = await fetch('http://localhost:5000/api/detect', {
  // ... or use a remote server
});
```

## 📱 Platform Support

- ✅ **Windows**: Fully supported
- ✅ **macOS**: Fully supported (requires accessibility permissions)
- ✅ **Linux**: Supported (X11 and Wayland)

## 🔐 Permissions Needed

### macOS
- Accessibility access (for global hotkeys)
- Screen recording (if using OCR in future)

### Windows
- None (works out of the box)

### Linux
- X11: Works automatically
- Wayland: May need additional permissions

## 🎯 Integration with Current Web App

Your **existing web application** remains unchanged! The overlay is a separate build that:

1. **Reuses your React components**
2. **Calls the same Flask API**
3. **Adds OS-level features** on top

You can run both simultaneously:
- Web app at `http://localhost:5173`
- Overlay as desktop app

## 📝 Next Steps

1. **Test overlay mode**: `npm run dev` in overlay folder
2. **Customize UI**: Edit `OverlayView.tsx` for your design
3. **Add OCR**: Integrate Tesseract.js for screen reading
4. **Build installer**: `npm run build:electron`
5. **Distribute**: Share the built app with users

## 💡 Tips

- Keep Flask backend running for both web and overlay
- Use the same `.env` configuration
- Overlay window is transparent - design accordingly
- Test on all target platforms before distribution

---

**Your web app and overlay can coexist!** Users can choose:
- 🌐 **Web version**: Full-featured app in browser
- 💻 **Overlay version**: Quick system-wide detection
