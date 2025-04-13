#!/usr/bin/env python3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class TodoApp:
    def __init__(self):
        self.window = TkinterDnD.Tk()
        self.window.title("Modern Todo List")
        self.window.geometry("1200x700")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('darkly')
        
        # Create main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create left sidebar
        self.sidebar = ttk.Frame(self.main_container, width=300)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        
        # Add buttons to sidebar
        self.add_task_btn = ttk.Button(
            self.sidebar,
            text="Add Task",
            command=self.show_add_task_dialog,
            style='primary.TButton'
        )
        self.add_task_btn.pack(pady=10, padx=10, fill="x")
        
        self.add_folder_btn = ttk.Button(
            self.sidebar,
            text="Add Folder",
            command=self.show_add_folder_dialog,
            style='primary.TButton'
        )
        self.add_folder_btn.pack(pady=10, padx=10, fill="x")
        
        # Create folder tree view
        self.folder_frame = ttk.Frame(self.sidebar)
        self.folder_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        self.folder_label = ttk.Label(self.folder_frame, text="Folders:")
        self.folder_label.pack(anchor="w")
        
        # Create Treeview for nested folders
        self.folder_tree = ttk.Treeview(
            self.folder_frame,
            selectmode="browse",
            show="tree"
        )
        self.folder_tree.pack(fill="both", expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_select)
        
        # Make folder tree draggable
        self.folder_tree.bind('<Button-1>', self.start_folder_drag)
        self.folder_tree.bind('<B1-Motion>', self.drag_folder)
        self.folder_tree.bind('<ButtonRelease-1>', self.drop_folder)
        
        # Add double-click for renaming
        self.folder_tree.bind('<Double-1>', self.rename_folder)
        
        # Create main content area
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side="right", fill="both", expand=True)
        
        # Initialize task list
        self.task_list = ttk.Frame(self.content)
        self.task_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for task list
        self.canvas = tk.Canvas(self.task_list)
        self.scrollbar = ttk.Scrollbar(self.task_list, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Load existing tasks and folders
        self.current_folder = "root"
        self.load_folders()
        self.load_tasks()
        
        # Drag and drop visual feedback
        self.drag_window = None
        self.drag_label = None
        self.drop_zone = None
        self.drop_zone_label = None
        
        # Create drop zone indicators
        self.create_drop_zones()
    
    def create_drop_zones(self):
        # Create drop zone for root level
        self.root_drop_zone = ttk.Frame(self.folder_frame, height=30)
        self.root_drop_zone.pack(fill="x", pady=5)
        self.root_drop_zone.pack_propagate(False)
        
        self.root_drop_label = ttk.Label(
            self.root_drop_zone,
            text="Drop here to move to root",
            style='primary.TLabel'
        )
        self.root_drop_label.pack(pady=5)
        
        # Initially hide drop zones
        self.root_drop_zone.pack_forget()
    
    def show_drop_zone(self, zone, text):
        if self.drop_zone:
            self.drop_zone.pack_forget()
        
        self.drop_zone = zone
        self.drop_zone_label = ttk.Label(
            zone,
            text=text,
            style='primary.TLabel'
        )
        self.drop_zone_label.pack(pady=5)
        zone.pack(fill="x", pady=5)
    
    def hide_drop_zone(self):
        if self.drop_zone:
            self.drop_zone.pack_forget()
            self.drop_zone = None
            self.drop_zone_label = None
    
    def create_drag_window(self, text):
        if self.drag_window:
            self.drag_window.destroy()
        
        self.drag_window = tk.Toplevel(self.window)
        self.drag_window.overrideredirect(True)  # Remove window decorations
        
        self.drag_label = ttk.Label(
            self.drag_window,
            text=text,
            style='primary.TLabel'
        )
        self.drag_label.pack(padx=10, pady=5)
    
    def update_drag_window(self, event):
        if self.drag_window:
            x = self.window.winfo_rootx() + event.x
            y = self.window.winfo_rooty() + event.y
            self.drag_window.geometry(f"+{x}+{y}")
    
    def show_add_folder_dialog(self):
        dialog = ttk.Toplevel(self.window)
        dialog.title("Add New Folder")
        dialog.geometry("500x300")
        dialog.resizable(True, True)
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Folder name
        name_label = ttk.Label(main_frame, text="Folder Name:")
        name_label.pack(pady=10)
        name_entry = ttk.Entry(main_frame, width=50)
        name_entry.pack(pady=5, fill="x")
        
        # Parent folder selection
        parent_label = ttk.Label(main_frame, text="Parent Folder:")
        parent_label.pack(pady=10)
        parent_var = tk.StringVar(value="root")
        parent_menu = ttk.Combobox(
            main_frame,
            textvariable=parent_var,
            values=self.get_all_folders(),
            state="readonly",
            width=47
        )
        parent_menu.pack(pady=5, fill="x")
        
        def save_folder():
            name = name_entry.get()
            parent = parent_var.get()
            
            if name:
                folder = {
                    "name": name,
                    "parent": parent,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.save_folder(folder)
                self.load_folders()
                name_entry.delete(0, tk.END)  # Clear the entry
                name_entry.focus()  # Focus back on the entry
            else:
                messagebox.showerror("Error", "Please enter a folder name")
        
        # Bind Enter key to save_folder
        name_entry.bind('<Return>', lambda e: save_folder())
        
        # Add button
        add_btn = ttk.Button(
            main_frame,
            text="Add",
            command=save_folder,
            style='primary.TButton'
        )
        add_btn.pack(pady=20)
        
        # Focus on the entry
        name_entry.focus()
    
    def get_all_folders(self):
        folders = []
        for folder in self.load_folders_data():
            folders.append(folder["name"])
        return folders
    
    def save_folder(self, folder):
        folders = self.load_folders_data()
        folders.append(folder)
        with open("data/folders.json", "w") as f:
            json.dump(folders, f, indent=4)
    
    def load_folders_data(self):
        try:
            with open("data/folders.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def load_folders(self):
        # Clear existing items
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)
        
        # Add all folders
        folders = self.load_folders_data()
        folder_dict = {}
        
        # First pass: create all folder entries
        for folder in folders:
            if folder["parent"] == "root":
                # Add root-level folders directly
                folder_id = self.folder_tree.insert(
                    "",
                    "end",
                    text=folder["name"],
                    values=[folder["name"]]
                )
                folder_dict[folder["name"]] = folder_id
            else:
                # Add subfolders under their parent
                parent_id = folder_dict.get(folder["parent"])
                if parent_id:
                    folder_id = self.folder_tree.insert(
                        parent_id,
                        "end",
                        text=folder["name"],
                        values=[folder["name"]]
                    )
                    folder_dict[folder["name"]] = folder_id
    
    def on_folder_select(self, event):
        selection = self.folder_tree.selection()
        if selection:
            self.current_folder = self.folder_tree.item(selection[0])["values"][0]
            self.load_tasks()
        else:
            self.current_folder = "root"
            self.load_tasks()
    
    def show_add_task_dialog(self):
        dialog = ttk.Toplevel(self.window)
        dialog.title("Add New Task")
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # Description row gets extra space
        
        # Task title
        title_label = ttk.Label(main_frame, text="Task Title:")
        title_label.grid(row=0, column=0, sticky="w", pady=10)
        title_entry = ttk.Entry(main_frame)
        title_entry.grid(row=0, column=1, sticky="ew", pady=10)
        
        # Task description
        desc_label = ttk.Label(main_frame, text="Description:")
        desc_label.grid(row=1, column=0, sticky="w", pady=10)
        desc_text = tk.Text(main_frame, height=6)
        desc_text.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Due date
        date_label = ttk.Label(main_frame, text="Due Date (YYYY-MM-DD):")
        date_label.grid(row=3, column=0, sticky="w", pady=10)
        date_entry = ttk.Entry(main_frame)
        date_entry.grid(row=3, column=1, sticky="ew", pady=10)
        
        def save_task():
            title = title_entry.get()
            description = desc_text.get("1.0", "end-1c")
            due_date = date_entry.get()
            
            if title and due_date:
                task = {
                    "title": title,
                    "description": description,
                    "due_date": due_date,
                    "completed": False,
                    "folder": self.current_folder,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.save_task(task)
                self.load_tasks()
                # Clear entries
                title_entry.delete(0, tk.END)
                desc_text.delete("1.0", tk.END)
                date_entry.delete(0, tk.END)
                title_entry.focus()  # Focus back on the title entry
            else:
                messagebox.showerror("Error", "Please fill in all required fields")
        
        # Bind Enter key to save_task
        title_entry.bind('<Return>', lambda e: save_task())
        date_entry.bind('<Return>', lambda e: save_task())
        
        # Add button
        add_btn = ttk.Button(
            main_frame,
            text="Add",
            command=save_task,
            style='primary.TButton'
        )
        add_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Focus on the title entry
        title_entry.focus()
        
        # Update window size to fit content
        dialog.update_idletasks()
        width = main_frame.winfo_reqwidth() + 40  # Add padding
        height = main_frame.winfo_reqheight() + 40
        dialog.geometry(f"{width}x{height}")
        
        # Make sure the window doesn't get too small
        dialog.minsize(400, 300)
    
    def save_task(self, task):
        tasks = self.load_tasks_data()
        tasks.append(task)
        with open("data/tasks/tasks.json", "w") as f:
            json.dump(tasks, f, indent=4)
    
    def load_tasks_data(self):
        try:
            with open("data/tasks/tasks.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def load_tasks(self):
        # Clear existing tasks
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        tasks = self.load_tasks_data()
        for task in tasks:
            if task["folder"] == self.current_folder:
                task_frame = ttk.Frame(self.scrollable_frame)
                task_frame.pack(fill="x", pady=5, padx=5)
                
                # Make task frame draggable
                task_frame.bind('<Button-1>', lambda e, t=task: self.start_drag(e, t))
                task_frame.bind('<B1-Motion>', lambda e, t=task: self.drag(e, t))
                task_frame.bind('<ButtonRelease-1>', lambda e, t=task: self.drop(e, t))
                
                # Task title and checkbox
                title_frame = ttk.Frame(task_frame)
                title_frame.pack(fill="x", pady=5)
                
                checkbox = ttk.Checkbutton(
                    title_frame,
                    text=task["title"],
                    command=lambda t=task: self.toggle_task(t)
                )
                checkbox.pack(side="left", padx=5)
                if task["completed"]:
                    checkbox.state(['selected'])
                
                # Add double-click for renaming
                checkbox.bind('<Double-1>', lambda e, t=task: self.rename_task(t))
                
                # Task details
                details_frame = ttk.Frame(task_frame)
                details_frame.pack(fill="x", pady=5)
                
                desc_label = ttk.Label(
                    details_frame,
                    text=f"Description: {task['description']}"
                )
                desc_label.pack(anchor="w", padx=5)
                
                date_label = ttk.Label(
                    details_frame,
                    text=f"Due: {task['due_date']}"
                )
                date_label.pack(anchor="w", padx=5)
    
    def start_drag(self, event, task):
        self.drag_data = task
        self.create_drag_window(task["title"])
        self.update_drag_window(event)
        # Show root drop zone
        self.root_drop_zone.pack(fill="x", pady=5)
    
    def drag(self, event, task):
        if hasattr(self, 'drag_data'):
            self.update_drag_window(event)
            
            # Check if over folder tree
            tree_x = self.folder_tree.winfo_rootx() - self.window.winfo_rootx()
            tree_y = self.folder_tree.winfo_rooty() - self.window.winfo_rooty()
            
            if (tree_x <= event.x <= tree_x + self.folder_tree.winfo_width() and
                tree_y <= event.y <= tree_y + self.folder_tree.winfo_height()):
                # Over folder tree
                target_item = self.folder_tree.identify_row(event.y + tree_y)
                if target_item:
                    self.folder_tree.selection_set(target_item)
                    self.hide_drop_zone()
                else:
                    self.folder_tree.selection_remove(self.folder_tree.selection())
                    self.show_drop_zone(self.root_drop_zone, "Drop here to move to root level")
            else:
                # Not over folder tree
                self.folder_tree.selection_remove(self.folder_tree.selection())
                self.show_drop_zone(self.root_drop_zone, "Drop here to move to root level")
    
    def drop(self, event, task):
        if hasattr(self, 'drag_data'):
            # Check if over folder tree
            tree_x = self.folder_tree.winfo_rootx() - self.window.winfo_rootx()
            tree_y = self.folder_tree.winfo_rooty() - self.window.winfo_rooty()
            
            if (tree_x <= event.x <= tree_x + self.folder_tree.winfo_width() and
                tree_y <= event.y <= tree_y + self.folder_tree.winfo_height()):
                # Over folder tree
                target_item = self.folder_tree.identify_row(event.y + tree_y)
                if target_item:
                    target_folder = self.folder_tree.item(target_item)["values"][0]
                    if target_folder != task["folder"]:
                        # Update task's folder
                        tasks = self.load_tasks_data()
                        for t in tasks:
                            if t["title"] == task["title"] and t["folder"] == task["folder"]:
                                t["folder"] = target_folder
                                break
                        with open("data/tasks/tasks.json", "w") as f:
                            json.dump(tasks, f, indent=4)
                        self.load_tasks()
            else:
                # Over root drop zone
                if self.drop_zone == self.root_drop_zone:
                    # Move task to root
                    tasks = self.load_tasks_data()
                    for t in tasks:
                        if t["title"] == task["title"] and t["folder"] == task["folder"]:
                            t["folder"] = "root"
                            break
                    with open("data/tasks/tasks.json", "w") as f:
                        json.dump(tasks, f, indent=4)
                    self.load_tasks()
            
            # Cleanup
            self.hide_drop_zone()
            self.root_drop_zone.pack_forget()
            if self.drag_window:
                self.drag_window.destroy()
                self.drag_window = None
            delattr(self, 'drag_data')
    
    def start_folder_drag(self, event):
        item = self.folder_tree.identify_row(event.y)
        if item:
            self.folder_drag_data = self.folder_tree.item(item)["values"][0]
            self.create_drag_window(self.folder_drag_data)
            self.update_drag_window(event)
            # Show root drop zone
            self.root_drop_zone.pack(fill="x", pady=5)
    
    def drag_folder(self, event):
        if hasattr(self, 'folder_drag_data'):
            self.update_drag_window(event)
            
            # Check if over folder tree
            tree_x = self.folder_tree.winfo_rootx() - self.window.winfo_rootx()
            tree_y = self.folder_tree.winfo_rooty() - self.window.winfo_rooty()
            
            if (tree_x <= event.x <= tree_x + self.folder_tree.winfo_width() and
                tree_y <= event.y <= tree_y + self.folder_tree.winfo_height()):
                # Over folder tree
                target_item = self.folder_tree.identify_row(event.y + tree_y)
                if target_item:
                    self.folder_tree.selection_set(target_item)
                    self.hide_drop_zone()
                else:
                    self.folder_tree.selection_remove(self.folder_tree.selection())
                    self.show_drop_zone(self.root_drop_zone, "Drop here to move to root level")
            else:
                # Not over folder tree
                self.folder_tree.selection_remove(self.folder_tree.selection())
                self.show_drop_zone(self.root_drop_zone, "Drop here to move to root level")
    
    def drop_folder(self, event):
        if hasattr(self, 'folder_drag_data'):
            # Check if over folder tree
            tree_x = self.folder_tree.winfo_rootx() - self.window.winfo_rootx()
            tree_y = self.folder_tree.winfo_rooty() - self.window.winfo_rooty()
            
            if (tree_x <= event.x <= tree_x + self.folder_tree.winfo_width() and
                tree_y <= event.y <= tree_y + self.folder_tree.winfo_height()):
                # Over folder tree
                target_item = self.folder_tree.identify_row(event.y + tree_y)
                if target_item:
                    target_folder = self.folder_tree.item(target_item)["values"][0]
                    if target_folder != self.folder_drag_data:
                        # Update folder's parent
                        folders = self.load_folders_data()
                        for folder in folders:
                            if folder["name"] == self.folder_drag_data:
                                folder["parent"] = target_folder
                                break
                        with open("data/folders.json", "w") as f:
                            json.dump(folders, f, indent=4)
                        self.load_folders()
            else:
                # Over root drop zone
                if self.drop_zone == self.root_drop_zone:
                    # Move folder to root level
                    folders = self.load_folders_data()
                    for folder in folders:
                        if folder["name"] == self.folder_drag_data:
                            folder["parent"] = "root"
                            break
                    with open("data/folders.json", "w") as f:
                        json.dump(folders, f, indent=4)
                    self.load_folders()
            
            # Cleanup
            self.hide_drop_zone()
            self.root_drop_zone.pack_forget()
            if self.drag_window:
                self.drag_window.destroy()
                self.drag_window = None
            delattr(self, 'folder_drag_data')
    
    def rename_folder(self, event):
        item = self.folder_tree.identify_row(event.y)
        if item:
            old_name = self.folder_tree.item(item)["values"][0]
            
            dialog = ttk.Toplevel(self.window)
            dialog.title("Rename Folder")
            dialog.geometry("300x150")
            
            # Create main frame with padding
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # New name entry
            name_label = ttk.Label(main_frame, text="New Name:")
            name_label.pack(pady=10)
            name_entry = ttk.Entry(main_frame)
            name_entry.insert(0, old_name)
            name_entry.pack(pady=5, fill="x")
            
            def save_rename():
                new_name = name_entry.get()
                if new_name and new_name != old_name:
                    folders = self.load_folders_data()
                    for folder in folders:
                        if folder["name"] == old_name:
                            folder["name"] = new_name
                            break
                    with open("data/folders.json", "w") as f:
                        json.dump(folders, f, indent=4)
                    self.load_folders()
                    dialog.destroy()
            
            # Bind Enter key
            name_entry.bind('<Return>', lambda e: save_rename())
            
            # Rename button
            rename_btn = ttk.Button(
                main_frame,
                text="Rename",
                command=save_rename,
                style='primary.TButton'
            )
            rename_btn.pack(pady=20)
            
            # Focus on the entry
            name_entry.focus()
    
    def rename_task(self, task):
        dialog = ttk.Toplevel(self.window)
        dialog.title("Rename Task")
        dialog.geometry("300x150")
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # New name entry
        name_label = ttk.Label(main_frame, text="New Title:")
        name_label.pack(pady=10)
        name_entry = ttk.Entry(main_frame)
        name_entry.insert(0, task["title"])
        name_entry.pack(pady=5, fill="x")
        
        def save_rename():
            new_title = name_entry.get()
            if new_title and new_title != task["title"]:
                tasks = self.load_tasks_data()
                for t in tasks:
                    if t["title"] == task["title"] and t["folder"] == task["folder"]:
                        t["title"] = new_title
                        break
                with open("data/tasks/tasks.json", "w") as f:
                    json.dump(tasks, f, indent=4)
                self.load_tasks()
                dialog.destroy()
        
        # Bind Enter key
        name_entry.bind('<Return>', lambda e: save_rename())
        
        # Rename button
        rename_btn = ttk.Button(
            main_frame,
            text="Rename",
            command=save_rename,
            style='primary.TButton'
        )
        rename_btn.pack(pady=20)
        
        # Focus on the entry
        name_entry.focus()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TodoApp()
    app.run() 