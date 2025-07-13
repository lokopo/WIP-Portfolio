# Modern Todo List App

A beautiful and intuitive todo list application built with CustomTkinter.

## Features

### 🎨 Modern UI
- Clean, modern interface with dark theme
- Card-based task display
- Intuitive navigation and controls

### 📁 Folder Organization
- Create custom folders to organize tasks
- Switch between folders easily
- "All Tasks" view to see everything at once

### ✅ Task Management
- Add, edit, and delete tasks
- Mark tasks as complete/incomplete
- Add descriptions and due dates
- Color-coded due dates (overdue, due today, due soon, etc.)

### 🔍 Search & Filter
- Real-time search through task titles and descriptions
- Filter by status: All, Pending, or Completed
- Smart sorting (pending tasks first, then by due date)

### 💾 Data Persistence
- Tasks and folders are automatically saved to JSON files
- No data loss between sessions

## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run_me.py
```

## Usage

### Adding Tasks
- Click the "+ Add Task" button
- Fill in the task title (required)
- Optionally add a description and due date
- Select a folder (or leave as "All Tasks")
- Click "Save"

### Managing Folders
- Click "+ New Folder" in the sidebar
- Enter a folder name
- Click "Save"

### Task Actions
- **Complete/Uncomplete**: Click the checkbox
- **Edit**: Click the pencil icon or click on the task title
- **Delete**: Click the trash icon

### Navigation
- Use the sidebar to switch between folders
- Use the search bar to find specific tasks
- Use the filter buttons to show only pending or completed tasks

## File Structure

```
To Do List/
├── run_me.py          # Main application
├── requirements.txt   # Python dependencies
├── README.md         # This file
└── data/             # Data storage
    ├── tasks.json    # Task data
    └── folders.json  # Folder data
```

## Improvements Made

This refactored version includes several major improvements over the original:

1. **Simplified UI**: Removed complex drag-and-drop in favor of simple, intuitive buttons
2. **Better Visual Hierarchy**: Tasks are displayed as cards with clear separation
3. **Enhanced Functionality**: Added search, filtering, and better task management
4. **Modern Design**: Uses CustomTkinter for a more contemporary look
5. **Improved UX**: Better dialogs, validation, and user feedback
6. **Cleaner Code**: More organized and maintainable codebase