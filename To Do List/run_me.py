#!/usr/bin/env python3
import customtkinter as ctk
import json
import os
from datetime import datetime, date
from tkinter import messagebox
import tkinter as tk
from typing import List, Dict, Optional

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TaskCard(ctk.CTkFrame):
    """A modern card widget for displaying individual tasks"""
    
    def __init__(self, master, task: Dict, on_toggle, on_edit, on_delete, **kwargs):
        super().__init__(master, **kwargs)
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.setup_ui()
        self.update_appearance()
    
    def setup_ui(self):
        # Main container with padding
        self.configure(fg_color=("gray90", "gray20"), corner_radius=10)
        
        # Header row with checkbox, title, and actions
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Checkbox
        self.checkbox_var = ctk.BooleanVar(value=self.task["completed"])
        self.checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=self.checkbox_var,
            command=self.toggle_task,
            width=20,
            height=20
        )
        self.checkbox.pack(side="left", padx=(0, 10))
        
        # Title (clickable for edit)
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.task["title"],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.title_label.bind("<Button-1>", lambda e: self.on_edit(self.task))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=30,
            command=lambda: self.on_edit(self.task),
            fg_color="transparent",
            hover_color=("gray80", "gray30")
        )
        edit_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            command=lambda: self.on_delete(self.task),
            fg_color="transparent",
            hover_color=("red", "darkred")
        )
        delete_btn.pack(side="left", padx=2)
        
        # Details section
        if self.task["description"] or self.task["due_date"]:
            details_frame = ctk.CTkFrame(self, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            # Description
            if self.task["description"]:
                desc_label = ctk.CTkLabel(
                    details_frame,
                    text=self.task["description"],
                    font=ctk.CTkFont(size=12),
                    anchor="w",
                    wraplength=400
                )
                desc_label.pack(anchor="w", pady=(0, 5))
            
            # Due date with color coding
            if self.task["due_date"]:
                try:
                    due_date = datetime.strptime(self.task["due_date"], "%Y-%m-%d").date()
                    today = date.today()
                    days_until = (due_date - today).days
                    
                    if days_until < 0:
                        date_color = "red"
                        date_text = f"Overdue by {abs(days_until)} days"
                    elif days_until == 0:
                        date_color = "orange"
                        date_text = "Due today"
                    elif days_until <= 3:
                        date_color = "yellow"
                        date_text = f"Due in {days_until} days"
                    else:
                        date_color = "green"
                        date_text = f"Due in {days_until} days"
                    
                    date_label = ctk.CTkLabel(
                        details_frame,
                        text=date_text,
                        font=ctk.CTkFont(size=11),
                        text_color=date_color
                    )
                    date_label.pack(anchor="w")
                except ValueError:
                    pass
    
    def toggle_task(self):
        self.task["completed"] = self.checkbox_var.get()
        self.on_toggle(self.task)
        self.update_appearance()
    
    def update_appearance(self):
        if self.task["completed"]:
            self.title_label.configure(text_color="gray")
            self.configure(fg_color=("gray85", "gray25"))
        else:
            self.title_label.configure(text_color=("black", "white"))
            self.configure(fg_color=("gray90", "gray20"))

class ModernTodoApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Modern Todo List")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Data
        self.current_folder = "All Tasks"
        self.tasks: List[Dict] = []
        self.folders: List[Dict] = []
        
        # Load data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        self.refresh_tasks()
    
    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left sidebar
        self.setup_sidebar(main_container)
        
        # Right content area
        self.setup_content_area(main_container)
    
    def setup_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=250, corner_radius=10)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        sidebar.grid_propagate(False)
        
        # Sidebar title
        title_label = ctk.CTkLabel(
            sidebar,
            text="📁 Folders",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20, padx=20)
        
        # Add folder button
        add_folder_btn = ctk.CTkButton(
            sidebar,
            text="+ New Folder",
            command=self.show_add_folder_dialog,
            height=35
        )
        add_folder_btn.pack(pady=(0, 20), padx=20, fill="x")
        
        # Folders list
        folders_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        folders_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # All Tasks button (always first)
        self.all_tasks_btn = ctk.CTkButton(
            folders_frame,
            text="📋 All Tasks",
            command=lambda: self.select_folder("All Tasks"),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            anchor="w",
            height=40
        )
        self.all_tasks_btn.pack(fill="x", pady=2)
        
        # Folder buttons will be added here
        self.folder_buttons = []
        self.refresh_folders()
    
    def setup_content_area(self, parent):
        content = ctk.CTkFrame(parent, corner_radius=10)
        content.grid(row=0, column=1, sticky="nsew")
        
        # Header
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        # Current folder title
        self.folder_title = ctk.CTkLabel(
            header_frame,
            text="All Tasks",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.folder_title.pack(side="left")
        
        # Add task button
        add_task_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Task",
            command=self.show_add_task_dialog,
            height=35
        )
        add_task_btn.pack(side="right")
        
        # Search bar
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_label = ctk.CTkLabel(search_frame, text="🔍 Search:")
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search tasks...",
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(content, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.filter_var = ctk.StringVar(value="all")
        
        all_btn = ctk.CTkRadioButton(
            filter_frame,
            text="All",
            variable=self.filter_var,
            value="all",
            command=self.refresh_tasks
        )
        all_btn.pack(side="left", padx=(0, 20))
        
        pending_btn = ctk.CTkRadioButton(
            filter_frame,
            text="Pending",
            variable=self.filter_var,
            value="pending",
            command=self.refresh_tasks
        )
        pending_btn.pack(side="left", padx=(0, 20))
        
        completed_btn = ctk.CTkRadioButton(
            filter_frame,
            text="Completed",
            variable=self.filter_var,
            value="completed",
            command=self.refresh_tasks
        )
        completed_btn.pack(side="left")
        
        # Tasks area
        tasks_frame = ctk.CTkFrame(content, fg_color="transparent")
        tasks_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tasks scrollable area
        self.tasks_scrollable = ctk.CTkScrollableFrame(
            tasks_frame,
            fg_color="transparent"
        )
        self.tasks_scrollable.pack(fill="both", expand=True)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            content,
            text="0 tasks",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(side="bottom", anchor="w", padx=20, pady=10)
    
    def load_data(self):
        """Load tasks and folders from JSON files"""
        # Load tasks
        try:
            with open("data/tasks.json", "r") as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []
        
        # Load folders
        try:
            with open("data/folders.json", "r") as f:
                self.folders = json.load(f)
        except FileNotFoundError:
            self.folders = []
    
    def save_data(self):
        """Save tasks and folders to JSON files"""
        # Ensure directories exist
        os.makedirs("data", exist_ok=True)
        
        # Save tasks
        with open("data/tasks.json", "w") as f:
            json.dump(self.tasks, f, indent=2)
        
        # Save folders
        with open("data/folders.json", "w") as f:
            json.dump(self.folders, f, indent=2)
    
    def refresh_folders(self):
        """Refresh the folder buttons in the sidebar"""
        # Remove existing folder buttons
        for btn in self.folder_buttons:
            btn.destroy()
        self.folder_buttons.clear()
        
        # Add folder buttons
        for folder in self.folders:
            btn = ctk.CTkButton(
                self.tasks_scrollable.master.master,  # Navigate to folders_frame
                text=f"📁 {folder['name']}",
                command=lambda f=folder: self.select_folder(f['name']),
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                anchor="w",
                height=40
            )
            btn.pack(fill="x", pady=2)
            self.folder_buttons.append(btn)
    
    def select_folder(self, folder_name: str):
        """Select a folder and refresh the task display"""
        self.current_folder = folder_name
        self.folder_title.configure(text=folder_name)
        
        # Update button appearances
        self.all_tasks_btn.configure(fg_color=("gray80", "gray30") if folder_name == "All Tasks" else "transparent")
        for btn in self.folder_buttons:
            btn.configure(fg_color="transparent")
        
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """Refresh the task display based on current folder and filter"""
        # Clear existing tasks
        for widget in self.tasks_scrollable.winfo_children():
            widget.destroy()
        
        # Filter tasks
        filtered_tasks = []
        for task in self.tasks:
            # Folder filter
            if self.current_folder != "All Tasks" and task.get("folder", "All Tasks") != self.current_folder:
                continue
            
            # Status filter
            if self.filter_var.get() == "pending" and task["completed"]:
                continue
            if self.filter_var.get() == "completed" and not task["completed"]:
                continue
            
            # Search filter
            search_term = self.search_entry.get().lower()
            if search_term:
                if (search_term not in task["title"].lower() and 
                    search_term not in task.get("description", "").lower()):
                    continue
            
            filtered_tasks.append(task)
        
        # Sort tasks (pending first, then by due date)
        filtered_tasks.sort(key=lambda x: (x["completed"], x.get("due_date", "9999-12-31")))
        
        # Create task cards
        for task in filtered_tasks:
            task_card = TaskCard(
                self.tasks_scrollable,
                task,
                on_toggle=self.toggle_task,
                on_edit=self.edit_task,
                on_delete=self.delete_task
            )
            task_card.pack(fill="x", pady=5)
        
        # Update status
        total_tasks = len([t for t in self.tasks if not t["completed"]])
        completed_tasks = len([t for t in self.tasks if t["completed"]])
        self.status_label.configure(text=f"{len(filtered_tasks)} tasks shown ({total_tasks} pending, {completed_tasks} completed)")
    
    def on_search(self, event):
        """Handle search input"""
        self.refresh_tasks()
    
    def show_add_task_dialog(self):
        """Show dialog to add a new task"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Add New Task")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Add New Task", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Task title
        title_entry_label = ctk.CTkLabel(main_frame, text="Task Title:")
        title_entry_label.pack(anchor="w", padx=20)
        
        title_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter task title...")
        title_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description (optional):")
        desc_label.pack(anchor="w", padx=20)
        
        desc_text = ctk.CTkTextbox(main_frame, height=100)
        desc_text.pack(fill="x", padx=20, pady=(0, 15))
        
        # Due date
        date_label = ctk.CTkLabel(main_frame, text="Due Date (YYYY-MM-DD, optional):")
        date_label.pack(anchor="w", padx=20)
        
        date_entry = ctk.CTkEntry(main_frame, placeholder_text="2024-12-31")
        date_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Folder selection
        folder_label = ctk.CTkLabel(main_frame, text="Folder:")
        folder_label.pack(anchor="w", padx=20)
        
        folder_var = ctk.StringVar(value=self.current_folder if self.current_folder != "All Tasks" else "")
        folder_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=folder_var,
            values=["All Tasks"] + [f["name"] for f in self.folders]
        )
        folder_menu.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_task():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Please enter a task title")
                return
            
            description = desc_text.get("1.0", "end-1c").strip()
            due_date = date_entry.get().strip()
            folder = folder_var.get()
            
            # Validate due date
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD)")
                    return
            
            # Create task
            task = {
                "title": title,
                "description": description,
                "due_date": due_date if due_date else None,
                "completed": False,
                "folder": folder if folder != "All Tasks" else "All Tasks",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.tasks.append(task)
            self.save_data()
            self.refresh_tasks()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        save_btn = ctk.CTkButton(buttons_frame, text="Save", command=save_task)
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel", command=cancel, fg_color="gray")
        cancel_btn.pack(side="right")
        
        # Focus on title entry
        title_entry.focus()
        title_entry.bind("<Return>", lambda e: save_task())
    
    def show_add_folder_dialog(self):
        """Show dialog to add a new folder"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Add New Folder")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Add New Folder", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Folder name
        name_label = ctk.CTkLabel(main_frame, text="Folder Name:")
        name_label.pack(anchor="w", padx=20)
        
        name_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter folder name...")
        name_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20)
        
        def save_folder():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a folder name")
                return
            
            # Check if folder already exists
            if any(f["name"] == name for f in self.folders):
                messagebox.showerror("Error", "A folder with this name already exists")
                return
            
            folder = {
                "name": name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.folders.append(folder)
            self.save_data()
            self.refresh_folders()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        save_btn = ctk.CTkButton(buttons_frame, text="Save", command=save_folder)
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel", command=cancel, fg_color="gray")
        cancel_btn.pack(side="right")
        
        # Focus on name entry
        name_entry.focus()
        name_entry.bind("<Return>", lambda e: save_folder())
    
    def toggle_task(self, task: Dict):
        """Toggle task completion status"""
        task["completed"] = not task["completed"]
        self.save_data()
        self.refresh_tasks()
    
    def edit_task(self, task: Dict):
        """Edit an existing task"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Edit Task")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Edit Task", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Task title
        title_entry_label = ctk.CTkLabel(main_frame, text="Task Title:")
        title_entry_label.pack(anchor="w", padx=20)
        
        title_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter task title...")
        title_entry.insert(0, task["title"])
        title_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description (optional):")
        desc_label.pack(anchor="w", padx=20)
        
        desc_text = ctk.CTkTextbox(main_frame, height=100)
        desc_text.insert("1.0", task.get("description", ""))
        desc_text.pack(fill="x", padx=20, pady=(0, 15))
        
        # Due date
        date_label = ctk.CTkLabel(main_frame, text="Due Date (YYYY-MM-DD, optional):")
        date_label.pack(anchor="w", padx=20)
        
        date_entry = ctk.CTkEntry(main_frame, placeholder_text="2024-12-31")
        if task.get("due_date"):
            date_entry.insert(0, task["due_date"])
        date_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Folder selection
        folder_label = ctk.CTkLabel(main_frame, text="Folder:")
        folder_label.pack(anchor="w", padx=20)
        
        current_folder = task.get("folder", "All Tasks")
        folder_var = ctk.StringVar(value=current_folder)
        folder_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=folder_var,
            values=["All Tasks"] + [f["name"] for f in self.folders]
        )
        folder_menu.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_changes():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Please enter a task title")
                return
            
            description = desc_text.get("1.0", "end-1c").strip()
            due_date = date_entry.get().strip()
            folder = folder_var.get()
            
            # Validate due date
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD)")
                    return
            
            # Update task
            task["title"] = title
            task["description"] = description
            task["due_date"] = due_date if due_date else None
            task["folder"] = folder if folder != "All Tasks" else "All Tasks"
            
            self.save_data()
            self.refresh_tasks()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        save_btn = ctk.CTkButton(buttons_frame, text="Save", command=save_changes)
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel", command=cancel, fg_color="gray")
        cancel_btn.pack(side="right")
        
        # Focus on title entry
        title_entry.focus()
        title_entry.bind("<Return>", lambda e: save_changes())
    
    def delete_task(self, task: Dict):
        """Delete a task"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task['title']}'?"):
            self.tasks.remove(task)
            self.save_data()
            self.refresh_tasks()
    
    def run(self):
        """Start the application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = ModernTodoApp()
    app.run() 