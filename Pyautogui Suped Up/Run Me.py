import customtkinter as ctk
from tkinter import messagebox, simpledialog
import pyautogui
import json
import time
import keyboard
import mouse
import threading
import os
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import tkinter as tk

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# File paths for saving data
COMMANDS_FILE = "commands.json"
WINDOW_STATE_FILE = "window_state.json"

class CommandType(Enum):
    CLICK = auto()
    TYPE = auto()
    HOTKEY = auto()
    DELAY = auto()

@dataclass
class Command:
    type: CommandType
    x: Optional[int] = None
    y: Optional[int] = None
    offset_x: int = 0
    offset_y: int = 0
    text: Optional[str] = None
    keys: Optional[str] = None
    seconds: Optional[float] = None

class PyAutoGUIEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("PyAutoGUI Command Editor")
        
        # Load window state if available
        self.load_window_state()
        
        # Store commands and markers
        self.commands = []
        self.markers = []
        self.marker_counter = 1
        self.running = False
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left panel for command list
        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Create scrollable frame for command list
        self.command_list_frame = ctk.CTkScrollableFrame(self.left_panel)
        self.command_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create right panel for controls
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="y", padx=5, pady=5)
        
        # Create buttons
        self.create_buttons()
        
        # Create status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_bar.pack(fill="x", padx=10, pady=5)
        
        # Screen marker windows
        self.screen_markers = []
        self.dragging_marker = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Load saved commands if they exist
        self.load_commands()
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_window_state(self):
        try:
            if os.path.exists(WINDOW_STATE_FILE):
                with open(WINDOW_STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.geometry(f"{state['width']}x{state['height']}+{state['x']}+{state['y']}")
                    if state.get('zoomed', False):
                        self.state('zoomed')
                    elif state.get('iconic', False):
                        self.state('iconic')
            else:
                # Default window size and position
                self.geometry("800x600")
                self.minsize(600, 400)
        except Exception as e:
            # Default window size and position if loading fails
            self.geometry("800x600")
            self.minsize(600, 400)
            print(f"Error loading window state: {e}")
            
    def save_window_state(self):
        try:
            state = {
                'width': self.winfo_width(),
                'height': self.winfo_height(),
                'x': self.winfo_x(),
                'y': self.winfo_y(),
                'zoomed': self.state() == 'zoomed',
                'iconic': self.state() == 'iconic'
            }
            with open(WINDOW_STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving window state: {e}")
            
    def on_closing(self):
        # Save window state before closing
        self.save_window_state()
        # Save commands
        self.save_commands()
        # Destroy the window
        self.destroy()
        
    def create_buttons(self):
        # Add Click Position button
        self.add_click_btn = ctk.CTkButton(
            self.right_panel,
            text="🖱️ Add Click Position",
            command=self.add_screen_click,
            fg_color="#4B8BBE",  # Python blue
            hover_color="#306998"  # Darker Python blue
        )
        self.add_click_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Type Text button
        self.add_type_btn = ctk.CTkButton(
            self.right_panel,
            text="⌨️ Add Type Text",
            command=self.add_type_command,
            fg_color="#2E8B57",  # Sea green
            hover_color="#1E6B47"  # Darker sea green
        )
        self.add_type_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Hotkey button
        self.add_hotkey_btn = ctk.CTkButton(
            self.right_panel,
            text="🔑 Add Hotkey",
            command=self.add_hotkey_command,
            fg_color="#8B4513",  # Saddle brown
            hover_color="#6B3513"  # Darker saddle brown
        )
        self.add_hotkey_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Delay button
        self.add_delay_btn = ctk.CTkButton(
            self.right_panel,
            text="⏱️ Add Delay",
            command=self.add_delay_command,
            fg_color="#4682B4",  # Steel blue
            hover_color="#3672A4"  # Darker steel blue
        )
        self.add_delay_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Run button
        self.run_btn = ctk.CTkButton(
            self.right_panel,
            text="▶️ Run",
            command=self.run_commands,
            fg_color="#228B22",  # Forest green
            hover_color="#128B12"  # Darker forest green
        )
        self.run_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Save button
        self.save_btn = ctk.CTkButton(
            self.right_panel,
            text="💾 Save",
            command=self.save_commands,
            fg_color="#4169E1",  # Royal blue
            hover_color="#3159D1"  # Darker royal blue
        )
        self.save_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Load button
        self.load_btn = ctk.CTkButton(
            self.right_panel,
            text="📂 Load",
            command=self.load_commands,
            fg_color="#9370DB",  # Medium purple
            hover_color="#8370CB"  # Darker medium purple
        )
        self.load_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Show/Hide Markers button
        self.show_markers_btn = ctk.CTkButton(
            self.right_panel,
            text="👁️ Show All Markers",
            command=self.toggle_markers,
            fg_color="#DAA520",  # Goldenrod
            hover_color="#CAA510"  # Darker goldenrod
        )
        self.show_markers_btn.pack(fill="x", padx=5, pady=5)

    def add_screen_click(self):
        # Get the current mouse position
        x, y = pyautogui.position()
        
        # Create the command
        cmd = Command(
            type=CommandType.CLICK,
            x=x,
            y=y
        )
        self.commands.append(cmd)
        
        # Create the marker at the current mouse position
        self.create_screen_marker(x, y, len(self.commands) - 1)
        
        # Update the command list
        self.update_command_list()
        
        # Update status
        self.status_bar.configure(text=f"Created marker at ({x}, {y}). Drag to adjust position.")

    def create_screen_marker(self, x, y, index):
        # Create a new window for the marker
        marker = ctk.CTkToplevel(self)
        marker.overrideredirect(True)  # Remove window decorations
        marker.attributes('-topmost', True)  # Keep on top
        marker.attributes('-alpha', 0.7)  # Semi-transparent
        
        # Position the window
        marker.geometry(f"40x40+{x-20}+{y-20}")
        
        # Create a canvas for the marker
        canvas = ctk.CTkCanvas(marker, width=40, height=40, bg='red', highlightthickness=1)
        canvas.pack(fill="both", expand=True)
        
        # Add the number
        canvas.create_text(20, 20, text=str(index + 1), fill='white', font=('Arial', 12, 'bold'))
        
        # Store the marker window and its index
        marker.index = index
        self.screen_markers.append(marker)
        
        # Add a close button
        close_btn = ctk.CTkButton(
            marker, 
            text="×", 
            width=10, 
            height=10,
            fg_color="red",
            hover_color="darkred",
            command=lambda: self.close_marker(marker)
        )
        close_btn.place(x=30, y=0)
        
        # Add offset button
        offset_btn = ctk.CTkButton(
            marker,
            text="⚙",
            width=10,
            height=10,
            fg_color="blue",
            hover_color="darkblue",
            command=lambda: self.set_marker_offset(marker)
        )
        offset_btn.place(x=0, y=0)
        
        # Bind mouse events for dragging
        marker.bind("<Button-1>", lambda e, m=marker: self.start_drag(e, m))
        marker.bind("<B1-Motion>", self.drag)
        marker.bind("<ButtonRelease-1>", self.stop_drag)
        
        return marker

    def set_marker_offset(self, marker):
        # Get the command for this marker
        cmd = self.commands[marker.index]
        
        # Create a dialog for offset input
        dialog = ctk.CTkToplevel(self)
        dialog.title("Set Marker Offset")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add X offset input
        x_frame = ctk.CTkFrame(dialog)
        x_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(x_frame, text="X Offset:").pack(side="left", padx=5)
        x_entry = ctk.CTkEntry(x_frame, width=100)
        x_entry.insert(0, str(cmd.offset_x))
        x_entry.pack(side="left", padx=5)
        
        # Add Y offset input
        y_frame = ctk.CTkFrame(dialog)
        y_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(y_frame, text="Y Offset:").pack(side="left", padx=5)
        y_entry = ctk.CTkEntry(y_frame, width=100)
        y_entry.insert(0, str(cmd.offset_y))
        y_entry.pack(side="left", padx=5)
        
        def apply_offset():
            try:
                cmd.offset_x = int(x_entry.get())
                cmd.offset_y = int(y_entry.get())
                self.update_command_list()
                self.status_bar.configure(text=f"Updated offset for marker {marker.index + 1} to ({cmd.offset_x}, {cmd.offset_y})")
                dialog.destroy()
            except ValueError:
                self.status_bar.configure(text="Please enter valid integer values for offsets")
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply_offset).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def start_drag(self, event, marker):
        self.dragging_marker = marker
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        if self.dragging_marker:
            x = self.dragging_marker.winfo_x() + (event.x - self.drag_start_x)
            y = self.dragging_marker.winfo_y() + (event.y - self.drag_start_y)
            self.dragging_marker.geometry(f"+{x}+{y}")
            
            # Update the command's position
            cmd = self.commands[self.dragging_marker.index]
            cmd.x = x + 20  # Add half the marker width
            cmd.y = y + 20  # Add half the marker height

    def stop_drag(self, event):
        self.dragging_marker = None
        self.update_command_list()

    def close_marker(self, marker):
        # Find the index of the marker in the screen_markers list
        try:
            index = self.screen_markers.index(marker)
            
            # Remove the command at this index
            if 0 <= index < len(self.commands):
                self.commands.pop(index)
            
            # Remove the marker from the screen_markers list
            self.screen_markers.pop(index)
            
            # Destroy the marker window
            marker.destroy()
            
            # Update remaining markers' indices
            for i, m in enumerate(self.screen_markers):
                m.index = i
            
            # Update the command list
            self.update_command_list()
            
            # Update status
            self.status_bar.configure(text=f"Removed marker {index + 1}")
        except ValueError:
            # Marker not found in screen_markers list
            marker.destroy()
            self.status_bar.configure(text="Marker removed")

    def toggle_markers(self):
        if self.show_markers_btn.cget("text") == "👁️ Show All Markers":
            self.show_all_markers()
            self.show_markers_btn.configure(text="👁️ Hide All Markers")
        else:
            self.hide_all_markers()
            self.show_markers_btn.configure(text="👁️ Show All Markers")

    def show_all_markers(self):
        for marker in self.screen_markers:
            marker.deiconify()
        self.status_bar.configure(text="Showing all markers")

    def hide_all_markers(self):
        for marker in self.screen_markers:
            marker.withdraw()
        self.status_bar.configure(text="Hiding all markers")

    def add_type_command(self):
        # Create input dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Type Command")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add text input
        ctk.CTkLabel(dialog, text="Enter text to type:").pack(pady=10)
        text_entry = ctk.CTkEntry(dialog, width=200)
        text_entry.pack(pady=5)
        
        def apply():
            text = text_entry.get()
            if text:
                cmd = Command(
                    type=CommandType.TYPE,
                    text=text
                )
                self.commands.append(cmd)
                self.update_command_list()
                dialog.destroy()
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def add_hotkey_command(self):
        # Create input dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Hotkey Command")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add hotkey input
        ctk.CTkLabel(dialog, text="Enter hotkey (e.g., 'ctrl+c'):").pack(pady=10)
        hotkey_entry = ctk.CTkEntry(dialog, width=200)
        hotkey_entry.pack(pady=5)
        
        def apply():
            keys = hotkey_entry.get()
            if keys:
                cmd = Command(
                    type=CommandType.HOTKEY,
                    keys=keys
                )
                self.commands.append(cmd)
                self.update_command_list()
                dialog.destroy()
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def add_delay_command(self):
        # Create input dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Delay Command")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add delay input
        ctk.CTkLabel(dialog, text="Enter delay in seconds:").pack(pady=10)
        delay_entry = ctk.CTkEntry(dialog, width=200)
        delay_entry.pack(pady=5)
        
        def apply():
            try:
                seconds = float(delay_entry.get())
                cmd = Command(
                    type=CommandType.DELAY,
                    seconds=seconds
                )
                self.commands.append(cmd)
                self.update_command_list()
                dialog.destroy()
            except ValueError:
                self.status_bar.configure(text="Please enter a valid number")
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def remove_command_at_index(self, index):
        if 0 <= index < len(self.commands):
            if self.commands[index].type == CommandType.CLICK:
                # Remove the corresponding screen marker if it exists
                if index < len(self.screen_markers):
                    self.screen_markers[index].destroy()
                    self.screen_markers.pop(index)
            self.commands.pop(index)
            self.update_command_list()
            self.status_bar.configure(text=f"Removed command {index + 1}")

    def remove_command(self):
        # Get the currently focused widget
        focused = self.focus_get()
        if isinstance(focused, ctk.CTkTextbox):
            # Find the index of the command
            for i, widget in enumerate(self.command_list_frame.winfo_children()):
                if widget.winfo_children()[0] == focused:
                    self.remove_command_at_index(i)
                    break

    def update_command_list(self):
        # Clear existing command boxes
        for widget in self.command_list_frame.winfo_children():
            widget.destroy()
        
        # Create a new text box for each command
        for i, cmd in enumerate(self.commands, 1):
            # Create a frame for each command
            cmd_frame = ctk.CTkFrame(self.command_list_frame)
            cmd_frame.pack(fill="x", padx=5, pady=2)
            
            # Create the text box
            cmd_text = ctk.CTkTextbox(cmd_frame, height=30, wrap="none")
            cmd_text.pack(side="left", fill="x", expand=True)
            
            # Add command text
            if cmd.type == CommandType.CLICK:
                offset_text = ""
                if cmd.offset_x != 0 or cmd.offset_y != 0:
                    offset_text = f" [offset: {cmd.offset_x}, {cmd.offset_y}]"
                cmd_text.insert("1.0", f"{i}. Click at ({cmd.x}, {cmd.y}){offset_text}")
                
                # Add offset button for click commands
                offset_btn = ctk.CTkButton(
                    cmd_frame,
                    text="⚙",
                    width=30,
                    height=30,
                    fg_color="blue",
                    hover_color="darkblue",
                    command=lambda idx=i-1: self.set_command_offset(idx)
                )
                offset_btn.pack(side="right", padx=2)
            elif cmd.type == CommandType.TYPE:
                cmd_text.insert("1.0", f"{i}. Type: {cmd.text}")
            elif cmd.type == CommandType.HOTKEY:
                cmd_text.insert("1.0", f"{i}. Hotkey: {cmd.keys}")
            elif cmd.type == CommandType.DELAY:
                cmd_text.insert("1.0", f"{i}. Delay: {cmd.seconds} seconds")
            
            # Make text box read-only
            cmd_text.configure(state="disabled")
            
            # Add move up button (except for first command)
            if i > 1:
                move_up_btn = ctk.CTkButton(
                    cmd_frame,
                    text="↑",
                    width=30,
                    height=30,
                    fg_color="gray",
                    hover_color="darkgray",
                    command=lambda idx=i-1: self.move_command_up(idx)
                )
                move_up_btn.pack(side="right", padx=2)
            
            # Add move down button (except for last command)
            if i < len(self.commands):
                move_down_btn = ctk.CTkButton(
                    cmd_frame,
                    text="↓",
                    width=30,
                    height=30,
                    fg_color="gray",
                    hover_color="darkgray",
                    command=lambda idx=i-1: self.move_command_down(idx)
                )
                move_down_btn.pack(side="right", padx=2)
            
            # Add edit button
            edit_btn = ctk.CTkButton(
                cmd_frame,
                text="✎",
                width=30,
                height=30,
                fg_color="green",
                hover_color="darkgreen",
                command=lambda idx=i-1: self.edit_command(idx)
            )
            edit_btn.pack(side="right", padx=2)
            
            # Add remove button
            remove_btn = ctk.CTkButton(
                cmd_frame,
                text="×",
                width=30,
                height=30,
                fg_color="red",
                hover_color="darkred",
                command=lambda idx=i-1: self.remove_command_at_index(idx)
            )
            remove_btn.pack(side="right", padx=2)

    def set_command_offset(self, index):
        # Get the command for this index
        cmd = self.commands[index]
        
        # Create a dialog for offset input
        dialog = ctk.CTkToplevel(self)
        dialog.title("Set Click Offset")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add X offset input
        x_frame = ctk.CTkFrame(dialog)
        x_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(x_frame, text="X Offset:").pack(side="left", padx=5)
        x_entry = ctk.CTkEntry(x_frame, width=100)
        x_entry.insert(0, str(cmd.offset_x))
        x_entry.pack(side="left", padx=5)
        
        # Add Y offset input
        y_frame = ctk.CTkFrame(dialog)
        y_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(y_frame, text="Y Offset:").pack(side="left", padx=5)
        y_entry = ctk.CTkEntry(y_frame, width=100)
        y_entry.insert(0, str(cmd.offset_y))
        y_entry.pack(side="left", padx=5)
        
        def apply_offset():
            try:
                cmd.offset_x = int(x_entry.get())
                cmd.offset_y = int(y_entry.get())
                self.update_command_list()
                self.status_bar.configure(text=f"Updated offset for click {index + 1} to ({cmd.offset_x}, {cmd.offset_y})")
                dialog.destroy()
            except ValueError:
                self.status_bar.configure(text="Please enter valid integer values for offsets")
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply_offset).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def move_command_up(self, index):
        if index > 0:
            # Swap commands
            self.commands[index], self.commands[index-1] = self.commands[index-1], self.commands[index]
            # Update command list
            self.update_command_list()
            self.status_bar.configure(text=f"Moved command {index+1} up")

    def move_command_down(self, index):
        if index < len(self.commands) - 1:
            # Swap commands
            self.commands[index], self.commands[index+1] = self.commands[index+1], self.commands[index]
            # Update command list
            self.update_command_list()
            self.status_bar.configure(text=f"Moved command {index+1} down")

    def edit_command(self, index):
        cmd = self.commands[index]
        
        # Create a dialog for editing
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Command")
        dialog.geometry("300x200")
        dialog.transient(self)
        
        if cmd.type == CommandType.CLICK:
            # Edit click position
            x_frame = ctk.CTkFrame(dialog)
            x_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(x_frame, text="X Position:").pack(side="left", padx=5)
            x_entry = ctk.CTkEntry(x_frame, width=100)
            x_entry.insert(0, str(cmd.x))
            x_entry.pack(side="left", padx=5)
            
            y_frame = ctk.CTkFrame(dialog)
            y_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(y_frame, text="Y Position:").pack(side="left", padx=5)
            y_entry = ctk.CTkEntry(y_frame, width=100)
            y_entry.insert(0, str(cmd.y))
            y_entry.pack(side="left", padx=5)
            
            def apply_edit():
                try:
                    cmd.x = int(x_entry.get())
                    cmd.y = int(y_entry.get())
                    self.update_command_list()
                    self.status_bar.configure(text=f"Updated click position to ({cmd.x}, {cmd.y})")
                    dialog.destroy()
                except ValueError:
                    self.status_bar.configure(text="Please enter valid integer values for positions")
        
        elif cmd.type == CommandType.TYPE:
            # Edit type text
            ctk.CTkLabel(dialog, text="Text to type:").pack(pady=10)
            text_entry = ctk.CTkEntry(dialog, width=200)
            text_entry.insert(0, cmd.text)
            text_entry.pack(pady=5)
            
            def apply_edit():
                cmd.text = text_entry.get()
                self.update_command_list()
                self.status_bar.configure(text=f"Updated type text to: {cmd.text}")
                dialog.destroy()
        
        elif cmd.type == CommandType.HOTKEY:
            # Edit hotkey
            ctk.CTkLabel(dialog, text="Hotkey (e.g., 'ctrl+c'):").pack(pady=10)
            hotkey_entry = ctk.CTkEntry(dialog, width=200)
            hotkey_entry.insert(0, cmd.keys)
            hotkey_entry.pack(pady=5)
            
            def apply_edit():
                cmd.keys = hotkey_entry.get()
                self.update_command_list()
                self.status_bar.configure(text=f"Updated hotkey to: {cmd.keys}")
                dialog.destroy()
        
        elif cmd.type == CommandType.DELAY:
            # Edit delay
            ctk.CTkLabel(dialog, text="Delay in seconds:").pack(pady=10)
            delay_entry = ctk.CTkEntry(dialog, width=200)
            delay_entry.insert(0, str(cmd.seconds))
            delay_entry.pack(pady=5)
            
            def apply_edit():
                try:
                    cmd.seconds = float(delay_entry.get())
                    self.update_command_list()
                    self.status_bar.configure(text=f"Updated delay to: {cmd.seconds} seconds")
                    dialog.destroy()
                except ValueError:
                    self.status_bar.configure(text="Please enter a valid number for delay")
        
        # Add apply button
        ctk.CTkButton(dialog, text="Apply", command=apply_edit).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def run_commands(self):
        if self.running:
            self.status_bar.configure(text="Already running commands")
            return
            
        self.running = True
        self.run_btn.configure(state="disabled")
        
        # Create progress window
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("Running Commands")
        progress_window.geometry("300x150")
        progress_window.transient(self)
        
        # Add progress label
        progress_label = ctk.CTkLabel(
            progress_window,
            text="Running commands...",
            font=("Helvetica", 16)
        )
        progress_label.pack(pady=20)
        
        # Add cancel button
        cancel_button = ctk.CTkButton(
            progress_window,
            text="Cancel",
            command=lambda: setattr(self, 'running', False)
        )
        cancel_button.pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        progress_window.update()
        progress_window.deiconify()
        progress_window.lift()
        progress_window.focus_force()
        progress_window.grab_set()
        
        def run_commands_thread():
            try:
                for i, cmd in enumerate(self.commands):
                    if not self.running:
                        break
                    # Use after() to safely update UI from thread
                    self.after(0, lambda: progress_label.configure(
                        text=f"Running command {i+1}/{len(self.commands)}"
                    ))
                    if cmd.type == CommandType.CLICK:
                        # Apply offsets when clicking
                        x = cmd.x + cmd.offset_x
                        y = cmd.y + cmd.offset_y
                        pyautogui.click(x, y)
                    elif cmd.type == CommandType.TYPE:
                        pyautogui.typewrite(cmd.text)
                    elif cmd.type == CommandType.HOTKEY:
                        pyautogui.hotkey(*cmd.keys.split("+"))
                    elif cmd.type == CommandType.DELAY:
                        time.sleep(cmd.seconds)
                self.after(0, progress_window.destroy)
            except Exception as e:
                self.after(0, lambda: self.status_bar.configure(text=f"Error: {str(e)}"))
            finally:
                self.running = False
                self.after(0, lambda: self.run_btn.configure(state="normal"))
                self.after(0, lambda: self.status_bar.configure(text="Ready"))
        
        threading.Thread(target=run_commands_thread, daemon=True).start()

    def save_commands(self):
        # Create a dialog for naming the script
        dialog = ctk.CTkToplevel(self)
        dialog.title("Save Script")
        dialog.geometry("300x150")
        dialog.transient(self)
        
        # Add script name input
        ctk.CTkLabel(dialog, text="Enter script name:").pack(pady=10)
        name_entry = ctk.CTkEntry(dialog, width=200)
        name_entry.pack(pady=5)
        
        def apply_save():
            script_name = name_entry.get().strip()
            if not script_name:
                self.status_bar.configure(text="Please enter a script name")
                return
            
            # Create scripts directory if it doesn't exist
            if not os.path.exists("scripts"):
                os.makedirs("scripts")
            
            # Save commands to a file with the given name
            file_path = os.path.join("scripts", f"{script_name}.json")
            
            # Convert commands to serializable format
            serializable_commands = []
            for cmd in self.commands:
                cmd_dict = {
                    "type": cmd.type.value,
                    "x": cmd.x,
                    "y": cmd.y,
                    "text": cmd.text,
                    "keys": cmd.keys,
                    "seconds": cmd.seconds,
                    "offset_x": cmd.offset_x,
                    "offset_y": cmd.offset_y
                }
                serializable_commands.append(cmd_dict)
            
            # Save marker positions
            marker_positions = []
            for marker in self.markers:
                marker_positions.append({
                    "x": marker.winfo_x(),
                    "y": marker.winfo_y()
                })
            
            # Save everything to file
            data = {
                "commands": serializable_commands,
                "marker_positions": marker_positions
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            
            self.status_bar.configure(text=f"Script '{script_name}' saved!")
            dialog.destroy()
        
        # Add apply button
        ctk.CTkButton(dialog, text="Save", command=apply_save).pack(pady=10)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def load_commands(self):
        # Create a dialog for selecting a script
        dialog = ctk.CTkToplevel(self)
        dialog.title("Load Script")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        # Create a frame for the list
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a scrollable frame for the list
        scroll_frame = ctk.CTkScrollableFrame(list_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        # Get list of saved scripts
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
        
        script_files = [f for f in os.listdir("scripts") if f.endswith(".json")]
        
        if not script_files:
            ctk.CTkLabel(scroll_frame, text="No saved scripts found").pack(pady=10)
        else:
            # Create a frame for the listbox
            listbox_frame = ctk.CTkFrame(scroll_frame)
            listbox_frame.pack(fill="both", expand=True, pady=5)
            
            # Create a listbox for scripts
            script_listbox = tk.Listbox(
                listbox_frame, 
                height=10,
                selectmode=tk.SINGLE,
                bg="#2b2b2b",  # Dark background
                fg="white",    # White text
                selectbackground="#1f538d",  # Selection color
                selectforeground="white",    # Selection text color
                font=("Helvetica", 12),
                highlightthickness=0,
                borderwidth=0
            )
            script_listbox.pack(fill="both", expand=True)
            
            # Add scripts to listbox
            for script_file in script_files:
                script_name = os.path.splitext(script_file)[0]
                script_listbox.insert(tk.END, script_name)
            
            # Create a frame for buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(fill="x", padx=10, pady=5)
            
            # Add Load button
            def load_selected():
                # Get selected script
                try:
                    selection = script_listbox.curselection()
                    if selection:
                        script_name = script_listbox.get(selection[0])
                        script_file = f"{script_name}.json"
                        self.load_script(script_file, dialog)
                    else:
                        self.status_bar.configure(text="Please select a script to load")
                except:
                    self.status_bar.configure(text="Please select a script to load")
            
            load_btn = ctk.CTkButton(
                button_frame,
                text="Load",
                command=load_selected,
                fg_color="#4169E1",  # Royal blue
                hover_color="#3159D1"  # Darker royal blue
            )
            load_btn.pack(side="left", padx=5)
            
            # Add Delete button
            def delete_selected():
                try:
                    selection = script_listbox.curselection()
                    if selection:
                        script_name = script_listbox.get(selection[0])
                        script_file = f"{script_name}.json"
                        file_path = os.path.join("scripts", script_file)
                        
                        # Create a custom confirmation dialog
                        confirm_dialog = ctk.CTkToplevel(dialog)
                        confirm_dialog.title("Confirm Delete")
                        confirm_dialog.geometry("300x150")
                        confirm_dialog.transient(dialog)
                        
                        # Add confirmation message
                        ctk.CTkLabel(
                            confirm_dialog, 
                            text=f"Are you sure you want to delete '{script_name}'?",
                            font=("Helvetica", 14)
                        ).pack(pady=20)
                        
                        # Create button frame
                        confirm_button_frame = ctk.CTkFrame(confirm_dialog)
                        confirm_button_frame.pack(fill="x", padx=20, pady=10)
                        
                        # Add Yes button
                        def confirm_delete():
                            os.remove(file_path)
                            self.status_bar.configure(text=f"Script '{script_name}' deleted!")
                            confirm_dialog.destroy()
                            dialog.destroy()
                            self.load_commands()  # Refresh the dialog
                        
                        yes_btn = ctk.CTkButton(
                            confirm_button_frame,
                            text="Yes",
                            command=confirm_delete,
                            fg_color="#DC143C",  # Crimson
                            hover_color="#CC143C"  # Darker crimson
                        )
                        yes_btn.pack(side="left", padx=5, expand=True)
                        
                        # Add No button
                        no_btn = ctk.CTkButton(
                            confirm_button_frame,
                            text="No",
                            command=confirm_dialog.destroy,
                            fg_color="#808080",  # Gray
                            hover_color="#707070"  # Darker gray
                        )
                        no_btn.pack(side="right", padx=5, expand=True)
                        
                        # Ensure window is visible before grabbing focus
                        confirm_dialog.update()
                        confirm_dialog.deiconify()
                        confirm_dialog.lift()
                        confirm_dialog.focus_force()
                        confirm_dialog.grab_set()
                    else:
                        self.status_bar.configure(text="Please select a script to delete")
                except:
                    self.status_bar.configure(text="Please select a script to delete")
            
            delete_btn = ctk.CTkButton(
                button_frame,
                text="Delete",
                command=delete_selected,
                fg_color="#DC143C",  # Crimson
                hover_color="#CC143C"  # Darker crimson
            )
            delete_btn.pack(side="left", padx=5)
            
            # Add Cancel button
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                fg_color="#808080",  # Gray
                hover_color="#707070"  # Darker gray
            )
            cancel_btn.pack(side="right", padx=5)
        
        # Ensure window is visible before grabbing focus
        dialog.update()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()
    
    def load_script(self, script_file, dialog):
        # Clear existing commands and markers
        self.commands.clear()
        for marker in self.markers:
            marker.destroy()
        self.markers.clear()
        self.screen_markers.clear()  # Clear screen_markers list as well
        
        # Load commands from file
        file_path = os.path.join("scripts", script_file)
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Restore commands
        for cmd_dict in data["commands"]:
            cmd = Command(
                type=CommandType(cmd_dict["type"]),
                x=cmd_dict["x"],
                y=cmd_dict["y"],
                text=cmd_dict["text"],
                keys=cmd_dict["keys"],
                seconds=cmd_dict["seconds"]
            )
            cmd.offset_x = cmd_dict["offset_x"]
            cmd.offset_y = cmd_dict["offset_y"]
            self.commands.append(cmd)
        
        # Create new markers for each click command
        for i, cmd in enumerate(self.commands):
            if cmd.type == CommandType.CLICK:
                # Create a new marker window at the saved position
                marker = self.create_screen_marker(cmd.x - 20, cmd.y - 20, i)  # Adjust for marker center
                self.markers.append(marker)
                self.screen_markers.append(marker)
        
        # Update command list
        self.update_command_list()
        
        # Close the dialog
        dialog.destroy()
        
        # Show success message
        script_name = os.path.splitext(script_file)[0]
        self.status_bar.configure(text=f"Script '{script_name}' loaded!")
        
        # Force show all markers and update button state
        self.show_all_markers()
        self.show_markers_btn.configure(text="👁️ Hide All Markers")

if __name__ == "__main__":
    app = PyAutoGUIEditor()
    app.mainloop() 