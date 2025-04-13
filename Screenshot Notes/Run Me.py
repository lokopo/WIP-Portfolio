#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QScrollArea, QTextEdit, QRubberBand, QMenu, QSizePolicy,
                            QToolBar, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QImage, QAction, QTransform, QCursor, QIcon
import os

class ImageCanvas(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.current_image = None
        self.is_selecting = False
        self.is_moving = False
        self.last_pos = None
        
    def mousePressEvent(self, event):
        if not self.current_image:
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.last_pos = event.pos()
            
            # Start selection
            self.is_selecting = True
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            
    def mouseMoveEvent(self, event):
        if not self.current_image:
            return
            
        if self.is_selecting:
            # Update selection rectangle
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
        elif self.is_moving and self.last_pos:
            # Move the image
            delta = event.pos() - self.last_pos
            self.move(self.pos() + delta)
            self.last_pos = event.pos()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_selecting:
                # Keep the selection visible
                self.is_selecting = False
            elif self.is_moving:
                self.is_moving = False
                self.last_pos = None
                
    def contextMenuEvent(self, event):
        if not self.current_image:
            return
            
        menu = QMenu(self)
        
        # Add crop action if there's a selection
        if self.rubberBand.isVisible() and self.rubberBand.geometry().width() > 0:
            crop_action = QAction("Crop", self)
            crop_action.triggered.connect(self.crop_image)
            menu.addAction(crop_action)
            
        # Add move action
        move_action = QAction("Move Image", self)
        move_action.triggered.connect(self.toggle_move_mode)
        menu.addAction(move_action)
        
        menu.exec(event.globalPos())
        
    def toggle_move_mode(self):
        self.is_moving = not self.is_moving
        if self.is_moving:
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            # Hide selection if visible
            if self.rubberBand.isVisible():
                self.rubberBand.hide()
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
    def crop_image(self):
        if self.rubberBand.isVisible() and self.current_image:
            rect = self.rubberBand.geometry()
            if rect.width() > 0 and rect.height() > 0:
                # Crop the image
                cropped = self.current_image.copy(rect)
                self.current_image = cropped
                pixmap = QPixmap.fromImage(cropped)
                self.setPixmap(pixmap)
                self.setFixedSize(pixmap.size())
                self.rubberBand.hide()
                return True
        return False

class NoteWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid black;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        
        self.dragging = False
        self.offset = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

class ScreenshotNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Notes")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Add toolbar actions
        self.load_action = QAction("Load Screenshot", self)
        self.load_action.triggered.connect(self.load_screenshot)
        self.toolbar.addAction(self.load_action)
        
        self.save_action = QAction("Save Image", self)
        self.save_action.triggered.connect(self.save_image)
        self.toolbar.addAction(self.save_action)
        
        self.add_note_action = QAction("Add Note", self)
        self.add_note_action.triggered.connect(self.add_note)
        self.toolbar.addAction(self.add_note_action)
        
        self.crop_action = QAction("Crop", self)
        self.crop_action.triggered.connect(self.crop_image)
        self.toolbar.addAction(self.crop_action)
        
        self.move_action = QAction("Move Image", self)
        self.move_action.triggered.connect(self.toggle_move_mode)
        self.toolbar.addAction(self.move_action)
        
        # Create scroll area for image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        
        # Create image canvas
        self.image_canvas = ImageCanvas()
        self.image_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_canvas)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Initialize notes list
        self.notes = []
        
    def load_screenshot(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Screenshot",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            # Load and display the image
            image = QImage(file_name)
            if not image.isNull():
                self.image_canvas.current_image = image
                pixmap = QPixmap.fromImage(image)
                self.image_canvas.setPixmap(pixmap)
                self.image_canvas.setFixedSize(pixmap.size())
                
                # Clear existing notes
                for note in self.notes:
                    note.deleteLater()
                self.notes.clear()
                
                self.statusBar.showMessage(f"Loaded image: {os.path.basename(file_name)}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")
            
    def save_image(self):
        if self.image_canvas.current_image:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            if file_name:
                # Create a pixmap from the current view
                pixmap = QPixmap(self.image_canvas.size())
                painter = QPainter(pixmap)
                self.image_canvas.render(painter)
                painter.end()
                pixmap.save(file_name)
                self.statusBar.showMessage(f"Saved image to: {os.path.basename(file_name)}")
        else:
            QMessageBox.warning(self, "Error", "No image to save")
            
    def add_note(self):
        if self.image_canvas.current_image:
            note = NoteWidget(self.image_canvas)
            note.setGeometry(50, 50, 200, 100)
            note.show()
            self.notes.append(note)
            self.statusBar.showMessage("Added note")
        else:
            QMessageBox.warning(self, "Error", "Load an image first")
            
    def crop_image(self):
        if self.image_canvas.current_image:
            if self.image_canvas.crop_image():
                self.statusBar.showMessage("Image cropped")
            else:
                QMessageBox.warning(self, "Error", "Select an area to crop first")
        else:
            QMessageBox.warning(self, "Error", "Load an image first")
            
    def toggle_move_mode(self):
        if self.image_canvas.current_image:
            self.image_canvas.toggle_move_mode()
            if self.image_canvas.is_moving:
                self.statusBar.showMessage("Move mode: ON - Click and drag to move the image")
            else:
                self.statusBar.showMessage("Move mode: OFF")
        else:
            QMessageBox.warning(self, "Error", "Load an image first")

def main():
    app = QApplication(sys.argv)
    window = ScreenshotNotesApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 