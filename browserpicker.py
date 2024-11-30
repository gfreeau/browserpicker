#!/usr/bin/env python3
import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Gdk
import subprocess

class BrowserPicker(Gtk.ApplicationWindow):
    def __init__(self, app, url=None):
        super().__init__(application=app, title="Select Browser to Open Link In")
        self.url = url
        self.active_buttons = []  # List to store buttons for active browser windows
        self.current_active_index = 0  # Index to track which button is active

        self.BROWSERS = {
            "Mozilla Firefox": "firefox",
            "Google Chrome": "google-chrome",
        }

        # Create main box with spacing and margins
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        self.set_child(box)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(key_controller)

        # Active windows section
        label = Gtk.Label(label="Active Browser Windows")
        label.set_halign(Gtk.Align.START)
        label.add_css_class("heading")
        box.append(label)

        self.window_group = None
        for title, window_id in self.get_browser_windows():
            button = Gtk.Button(label=title)
            button.connect('clicked', self.on_window_selected, window_id)
            box.append(button)
            self.active_buttons.append((button, window_id))

        if self.active_buttons:
            self.active_buttons[0][0].grab_focus()
            self.active_buttons[0][0].add_css_class("suggested-action")

        # New browser section
        label = Gtk.Label(label="Launch New Browser")
        label.set_halign(Gtk.Align.START)
        label.add_css_class("heading")
        box.append(label)

        for name, command in self.BROWSERS.items():
            button = Gtk.Button(label=f"Open in {name}")
            button.connect('clicked', self.on_launch_browser, command)
            box.append(button)

        instruction_label = Gtk.Label(
            label="Use ↑/↓ to navigate, Enter to select, or click buttons to open a browser."
        )
        instruction_label.add_css_class("dim-label")
        instruction_label.set_margin_top(12)
        box.append(instruction_label)

    def get_browser_windows(self):
        """Get active browser windows using xdotool."""
        cmd = ['xdotool', 'search', '--name', 'Mozilla Firefox|Google Chrome']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        window_ids = result.stdout.decode('utf-8').rstrip().split("\n")

        windows = []
        for id in window_ids:
            if id:  # Skip empty IDs
                cmd = ['xdotool', 'getwindowname', id]
                result = subprocess.run(cmd, stdout=subprocess.PIPE)
                title = result.stdout.decode('utf-8').rstrip()
                windows.append((title, id))
        return windows

    def on_window_selected(self, button, window_id):
        """Activate the selected window."""
        subprocess.run(['xdotool', 'windowactivate', '--sync', window_id])
        if self.url:
            cmd = [
                'xdotool', 'key', '--clearmodifiers', '--window', window_id, 'ctrl+t',
                'sleep', '.1',
                'type', '--clearmodifiers', self.url
            ]
            subprocess.run(cmd)
            
            cmd = ['xdotool', 'key', '--clearmodifiers', '--window', window_id, 'Return']
            subprocess.run(cmd)
        self.close()

    def on_launch_browser(self, button, browser_command):
        """Launch a new browser instance."""
        try:
            if browser_command == "google-chrome":
                cmd = [browser_command, "--show-profile-picker"]
                if self.url:
                    cmd.append(self.url)
                subprocess.Popen(cmd)
            else:
                cmd = [browser_command]
                if self.url:
                    cmd.append(self.url)
                subprocess.Popen(cmd)
            self.close()
        except FileNotFoundError:
            print(f"Error: {browser_command} is not installed or not in PATH.")

    def on_key_press(self, controller, keyval, keycode, state):
        """Handle key press events for keyboard navigation."""
        if not self.active_buttons:
            return False

        if keyval == Gdk.KEY_Down or keyval == Gdk.KEY_Up:
            # Remove suggested-action class from current button
            self.active_buttons[self.current_active_index][0].remove_css_class("suggested-action")
            
            # Update index
            if keyval == Gdk.KEY_Down:
                self.current_active_index += 1
                if self.current_active_index >= len(self.active_buttons):
                    self.current_active_index = 0  # Wrap around
            else:  # Up
                self.current_active_index -= 1
                if self.current_active_index < 0:
                    self.current_active_index = len(self.active_buttons) - 1  # Wrap around
            
            # Add suggested-action class to new button and focus it
            button = self.active_buttons[self.current_active_index][0]
            button.add_css_class("suggested-action")
            button.grab_focus()
            return True
            
        elif keyval == Gdk.KEY_Return:
            if self.active_buttons:
                button, window_id = self.active_buttons[self.current_active_index]
                self.on_window_selected(button, window_id)
            return True
            
        return False

class BrowserPickerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.x.browser-picker",
                        flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

    def do_activate(self):
        win = BrowserPicker(self)
        win.present()

    def do_command_line(self, command_line):
        args = command_line.get_arguments()
        if len(args) > 1:
            # First argument is the program name, second would be the URL
            win = BrowserPicker(self, args[1])
        else:
            win = BrowserPicker(self)
        win.present()
        return 0

if __name__ == "__main__":
    app = BrowserPickerApp()
    app.run(sys.argv)
