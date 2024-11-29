# **Browser Picker Script**

## **Overview**

The **Browser Picker Script** allows you to dynamically select which browser to use when opening links in Linux. It's useful if you use multiple browsers or browser profiles such as chrome profiles and want to open links in a specific browser each time. It's been tested on Ubuntu, Debian and Mint.

### **Key Features**
- Dynamically choose between active browser windows (e.g., Chrome, Firefox).
- Support for opening URLs in new browser instances if no active windows are found.
- Search functionality for filtering active browser windows.
- Fully configurable to set as the default browser for your system.

---

## **Installation**

### **Prerequisites**

1. **Browsers**
   - **Google Chrome**: Download and install from [Google Chrome Official Website](https://www.google.com/chrome/)
   - **Mozilla Firefox**: Install via package manager:
     ```bash
     sudo apt install firefox
     ```

2. **Dependencies**
   ```bash
   sudo apt install python3 python3-tk xdotool
   ```

### **Setup Steps**

1. **Download and Save the Script**
   - Save `browserpicker.py` in a directory (e.g., `~/bin/`)
   ```bash
   mkdir -p ~/bin
   # Copy browserpicker.py to ~/bin/
   ```

2. **Make the Script Executable**
   ```bash
   chmod +x ~/bin/browserpicker.py
   ```

3. **Create Desktop Entry**
   Create the file `~/.local/share/applications/browserpicker.desktop`:

   Add the following contents (replace `<your-username>`):
   ```ini
   [Desktop Entry]
   Version=1.0
   Name=Browser Picker
   Comment=Select which browser to use
   Exec=/usr/bin/env python3 /home/<your-username>/bin/browserpicker.py %u
   Terminal=false
   Type=Application
   Icon=web-browser
   Categories=Network;WebBrowser;
   MimeType=x-scheme-handler/http;x-scheme-handler/https;
   ```

4. **Update Desktop Database**
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

5. **Set as Default Browser**
   ```bash
   # Set as default browser
   xdg-settings set default-web-browser browserpicker.desktop
   
   # Associate with HTTP(S) URLs
   xdg-mime default browserpicker.desktop x-scheme-handler/http
   xdg-mime default browserpicker.desktop x-scheme-handler/https
   ```

6. **Verify Installation**
   ```bash
   xdg-settings get default-web-browser
   # Should output: browserpicker.desktop
   ```

## **Usage**

### **Basic Usage**
Run the script directly with a URL:
```bash
./browserpicker.py https://example.com
```

### **Interface**
The Browser Picker provides an intuitive GUI with the following features:

- **Active Window Selection**: Shows all currently open browser windows
- **Search Functionality**: Filter active windows using the search bar
- **New Browser Options**: Launch new instances of installed browsers
- **Keyboard Navigation**:
  - `↑`/`k`: Select previous option
  - `↓`/`j`: Select next option
  - `Enter`: Open URL in selected browser/window

### **Supported Browsers**
- Mozilla Firefox
- Google Chrome (includes profile picker support)

## **Configuration**

The script can be customized by modifying the following variables in `browserpicker.py`:

```python
SEARCH_STRING = 'Mozilla Firefox|Google Chrome'  # Modify to search for different browser windows
BROWSERS = {
    "Mozilla Firefox": "firefox",
    "Google Chrome": "google-chrome",
}  # Add or modify browser commands
```

### **Adding Additional Browsers**

The script can be configured to support other browsers like Brave. Simply modify your `browserpicker.py`:

```python:browserpicker.py
# Modify these variables to add support for additional browsers
SEARCH_STRING = 'Mozilla Firefox|Google Chrome|Brave Browser'
BROWSERS = {
    "Mozilla Firefox": "firefox",
    "Google Chrome": "google-chrome",
    "Brave Browser": "brave-browser"  # Add additional browsers here
}
```

The browser command (right side of the dictionary) should match the executable name in your system PATH.

## **Technical Details**

- Uses `xdotool` for window management and keyboard simulation
- Automatically detects and positions the window on the active monitor
- Supports multi-monitor setups
- Handles browser window activation across different virtual desktops

## **Contributing**

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

## **Troubleshooting**

### Common Issues
1. **Window not appearing on correct monitor**
   - Ensure xrandr is working correctly
   - Check monitor configuration in system settings

2. **Browser not launching**
   - Verify browser executables are in your system PATH
   - Check that browser packages are properly installed

3. **Keyboard shortcuts not working**
   - Ensure no conflicts with system shortcuts
   - Verify tkinter installation is complete

