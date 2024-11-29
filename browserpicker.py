#!/usr/bin/env python3

import sys
import tkinter
import subprocess

URL = sys.argv[1] if len(sys.argv) > 1 else None
SEARCH_STRING = 'Mozilla Firefox|Google Chrome'
BROWSERS = {
    "Mozilla Firefox": "firefox",
    "Google Chrome": "google-chrome",
}

def get_options():
    """Get active browser windows using xdotool."""
    cmd = ['xdotool', 'search', '--name', SEARCH_STRING]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    window_ids = result.stdout.decode('utf-8').rstrip().split("\n")

    options = []
    for id in window_ids:
        if id:  # Skip empty IDs
            cmd = ['xdotool', 'getwindowname', id]
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            title = result.stdout.decode('utf-8').rstrip()
            options.append((title, id))

    return options

def launch_browser(browser_command, url=None):
    """Launch the specified browser with the given URL."""
    try:
        if browser_command == "google-chrome":
            cmd = [browser_command, "--show-profile-picker"]
            if url:
                cmd.append(url)
            subprocess.Popen(cmd)
        else:
            if url:
                subprocess.Popen([browser_command, url])
            else:
                subprocess.Popen([browser_command])
        print(f"Launching {browser_command}...")
        kill_window()  # Close the picker window after launching
    except FileNotFoundError:
        print(f"Error: {browser_command} is not installed or not in PATH.")

def get_active_monitor_geometry():
    """Get the geometry of the monitor where the mouse pointer is located."""
    # Get mouse position
    cmd = ['xdotool', 'getmouselocation', '--shell']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').splitlines()
    
    mouse_x, mouse_y = None, None
    for line in output:
        if line.startswith("X="):
            mouse_x = int(line.split("=")[1])
        if line.startswith("Y="):
            mouse_y = int(line.split("=")[1])
    
    if mouse_x is None or mouse_y is None:
        return None  # Fallback to default behavior if mouse position is not found

    # Get monitor geometry from xrandr
    cmd = ['xrandr']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    xrandr_output = result.stdout.decode('utf-8').splitlines()

    for line in xrandr_output:
        if " connected" in line:
            # Extract geometry, e.g., "1920x1080+0+0"
            parts = line.split()
            for part in parts:
                if "x" in part and "+" in part:  # Ensure it's a valid geometry string
                    res, offset_x, offset_y = part.split("+")
                    width, height = map(int, res.split("x"))
                    offset_x, offset_y = int(offset_x), int(offset_y)

                    # Check if the mouse pointer is within this monitor's bounds
                    if offset_x <= mouse_x < offset_x + width and offset_y <= mouse_y < offset_y + height:
                        return width, height, offset_x, offset_y

    return None  # Fallback if no monitor geometry matches

def kill_window(event=None):
    root.destroy()

def select_prev_option(event):
    val = curr_var.get()
    idx = [i for i, option in enumerate(OPTIONS) if option[1] == val][0]
    if idx > 0:
        curr_var.set(OPTIONS[idx-1][1])

def select_next_option(event):
    val = curr_var.get()
    idx = [i for i, option in enumerate(OPTIONS) if option[1] == val][0]
    if idx < len(OPTIONS)-1:
        curr_var.set(OPTIONS[idx+1][1])

def execute_option(event=None):
    selected_option = curr_var.get()

    # Handle selecting an active browser window
    window_id = selected_option
    cmd = ['xdotool', 'get_desktop']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    current_desktop = int(result.stdout.decode('utf-8').rstrip())

    cmd = ['xdotool', 'get_desktop_for_window', window_id]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    window_desktop = int(result.stdout.decode('utf-8').rstrip())

    if current_desktop != window_desktop:
        cmd = ['xdotool', 'set_desktop', str(window_desktop)]
        subprocess.run(cmd, stdout=subprocess.PIPE)

    cmd = ['xdotool', 'windowactivate', '--sync', window_id]
    subprocess.run(cmd, stdout=subprocess.PIPE)

    if URL:
        cmd = [
            'xdotool', 'key', '--clearmodifiers', '--window', window_id, 'ctrl+t',
            'sleep', '.1',
            'type', '--clearmodifiers', URL
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE)

        cmd = ['xdotool', 'key', '--clearmodifiers', '--window', window_id, 'Return']
        subprocess.run(cmd, stdout=subprocess.PIPE)

    kill_window()

# Initialize GUI
root = tkinter.Tk()
root.title("Select Browser to Open Link")

# Get active browser windows
OPTIONS = get_options()

# Position window on the active monitor
monitor_geometry = get_active_monitor_geometry()
if monitor_geometry:
    monitor_width, monitor_height, monitor_offset_x, monitor_offset_y = monitor_geometry
    window_width = 800
    window_height = 400
    x = monitor_offset_x + (monitor_width - window_width) // 2
    y = monitor_offset_y + (monitor_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
else:
    root.geometry("800x400")  # Default size and position fallback

# Add active browser options
if OPTIONS:
    curr_var = tkinter.StringVar()
    curr_var.set(OPTIONS[0][1])

    # Add section label for active browsers
    active_label = tkinter.Label(
        root,
        text="Active Browser Windows:",
        font=("Arial", 12, "bold"),
        anchor=tkinter.W
    )
    active_label.pack(pady=(10,5), padx=10, fill=tkinter.X)

    # Add a search bar if active browsers exist
    search_var = tkinter.StringVar()
    search_entry = tkinter.Entry(root, textvariable=search_var, font=("Arial", 14), width=40)
    search_entry.insert(0, "Search active windows...")
    search_entry.pack(pady=(0,10))
    search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tkinter.END))
    def filter_list(event):
        search_term = search_var.get().lower()
        for button in buttons:
            if search_term in button.cget("text").lower():
                button.pack(anchor=tkinter.W, fill=tkinter.X, expand=True)
            else:
                button.pack_forget()
    search_entry.bind("<KeyRelease>", filter_list)

    # Create frame for active browsers
    button_frame = tkinter.Frame(root)
    button_frame.pack(fill=tkinter.BOTH, expand=True)

    buttons = []
    for text, mode in OPTIONS:
        b = tkinter.Radiobutton(
            button_frame,
            text=text,
            variable=curr_var,
            value=mode,
            indicatoron=0,
            font=("Helvetica", 14, "bold"),
            anchor=tkinter.W,
            command=execute_option
        )
        b.pack(fill=tkinter.X, pady=5, padx=5)
        buttons.append(b)

# Add section label for new browser launches
new_browser_label = tkinter.Label(
    root,
    text="Launch New Browser Instance:",
    font=("Arial", 12, "bold"),
    anchor=tkinter.W
)
new_browser_label.pack(pady=(20,5), padx=10, fill=tkinter.X)

# Add buttons for launching new browsers
def add_launch_button(browser_name):
    browser_command = BROWSERS[browser_name]
    btn = tkinter.Button(
        root,
        text=f"Open in {browser_name}",
        font=("Helvetica", 14, "bold"),
        command=lambda: launch_browser(browser_command, URL),
    )
    btn.pack(pady=5, padx=10, fill=tkinter.X)

for browser in BROWSERS:
    add_launch_button(browser)

# Footer with instructions
footer = tkinter.Label(
    root,
    text="Use ↑/↓ to navigate, Enter to select, or click buttons to open a browser.",
    font=("Arial", 10, "italic"),
    fg="gray"
)
footer.pack(side=tkinter.BOTTOM, pady=10)

# Keyboard bindings for navigation
if OPTIONS:
    root.bind("<j>", select_next_option)
    root.bind("<Down>", select_next_option)
    root.bind("<k>", select_prev_option)
    root.bind("<Up>", select_prev_option)
    root.bind("<Return>", execute_option)

root.mainloop()

