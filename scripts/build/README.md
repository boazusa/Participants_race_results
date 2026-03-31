# Build Scripts for Race Results App

## 📁 Files in this folder:

### 🚀 Build Scripts:
- **`build_exe.py`** - Production version (silent, no console)
- **`build_exe_dev.py`** - Development version (console visible for debugging)
- **`build_exe_spec.py`** - Advanced PyInstaller spec file

### 📄 Generated Spec Files:
- **`RaceResultsApp.spec`** - Generated spec for production build
- **`RaceResultsAppDev.spec`** - Generated spec for development build  
- **`RaceResultsAppOptimized.spec`** - Generated spec for optimized build

## 🎯 How to Use:

### For Production (Silent - for users):
```bash
python build_exe.py
```
- Creates: `dist/RaceResultsAppOptimized.exe`
- Size: ~38MB
- Console: Hidden
- Use: Distribute to end users

### For Development (Console visible - for you):
```bash
python build_exe_dev.py
```
- Creates: `dist/RaceResultsAppDev.exe`
- Size: ~38MB
- Console: Visible (shows Flask output)
- Use: Development and debugging

### Advanced (Using spec file):
```bash
pyinstaller build_exe_spec.py
```
- Uses custom PyInstaller configuration
- For advanced users only

## 📂 Where to find executables:
After building, check the `../dist/` folder for:
- `RaceResultsAppOptimized.exe` (production)
- `RaceResultsAppDev.exe` (development)

## ⚡ Quick Start:
1. Open command prompt in this folder
2. Run: `python build_exe_dev.py` (for development)
3. Find your executable in `../dist/`
4. Double-click to run your app!

## 🛠️ Requirements:
- Python 3.9+
- PyInstaller: `pip install pyinstaller`

## 📊 Executable Sizes:
- Production: ~38MB (silent)
- Development: ~38MB (console visible)
- Both include all dependencies (pandas, flask, etc.)

## 🎉 Ready to distribute!
Your Flask race results app is now a standalone Windows executable!
