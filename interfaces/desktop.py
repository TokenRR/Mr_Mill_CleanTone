import os
import shutil
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QListWidget, QLabel,
                             QGridLayout, QSplitter, QMessageBox, QFrame, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QDir, QSize, QPoint, QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap, QDesktopServices, QFont


# Define the black and yellow theme for dark mode
DARK_THEME = {
    "background": "#0F0F0F",
    "button_background": "#FFB700",
    "border": "#FFD000",
    "text_color": "#0F0F0F",
    "run_button_color": "#FFB700",
    "file_list_text_color": "#FFFFFF",  # White text for the file list in dark mode
    "drop_label_text_color": "#FFFFFF",  # White text for the drop area in dark mode
    "message_box_text_color": "#FFFFFF"  # White text for message boxes in dark mode
}

# Define the white and blue theme for light mode
LIGHT_THEME = {
    "background": "#FFFFFF",
    "button_background": "#1a3597",
    "border": "#1a3597",
    "text_color": "#FFFFFF",
    "run_button_color": "#1a3597",
    "file_list_text_color": "#000000",  # Black text for the file list in light mode
    "drop_label_text_color": "#000000",  # Black text for the drop area in light mode
    "message_box_text_color": "#000000"  # Black text for message boxes in light mode
}


class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon_type, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('interfaces/images/icon.ico'))

        # Set the layout for the custom message box
        layout = QVBoxLayout()

        # Create a horizontal layout for the icon and message
        h_layout = QHBoxLayout()

        # Add the icon to the message box
        icon_label = QLabel()
        if icon_type == 'warning':
            icon_label.setPixmap(QPixmap('interfaces/images/warning_icon.png').scaled(32, 32, Qt.KeepAspectRatio))
        elif icon_type == 'error':
            icon_label.setPixmap(QPixmap('interfaces/images/error_icon.png').scaled(32, 32, Qt.KeepAspectRatio))
        else:
            icon_label.setPixmap(QPixmap('interfaces/images/info_icon.png').scaled(32, 32, Qt.KeepAspectRatio))

        # Add icon to the layout
        h_layout.addWidget(icon_label)

        # Add the message text
        self.label = QLabel(message)
        self.label.setStyleSheet(f"color: {current_theme['drop_label_text_color']};")
        h_layout.addWidget(self.label)

        # Add the horizontal layout (icon + message) to the main layout
        layout.addLayout(h_layout)

        # Add an OK button with the same style as the "Run" button
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(f"""
            background-color: {current_theme['run_button_color']}; 
            color: {current_theme['text_color']}; 
            border-radius: 10px;
            padding: 5px;
        """)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {current_theme['background']};")
        self.setFixedSize(350, 150)


class VideoUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Uploader')
        self.setGeometry(200, 200, 800, 600)

        # Set window icon
        self.setWindowIcon(QIcon('interfaces/images/icon.ico'))

        # Disable the native title bar to create a custom one
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setMinimumSize(1000, 600)  # Allow manual resizing

        # Variables for window dragging
        self.old_pos = None

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Custom title bar
        self.create_custom_title_bar(main_layout)

        # Create a splitter to make areas resizable
        splitter = QSplitter(Qt.Horizontal)

        # Directory selection layout
        self.dir_button = QPushButton('Select Directory')
        self.dir_button.clicked.connect(self.select_directory)

        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_file)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh_directory)

        # Run and Language switch buttons
        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run_process)

        self.language_button = QPushButton('Switch to Ukrainian')
        self.language_button.clicked.connect(self.switch_language)
        self.language = 'EN'

        # Make all buttons the same height as the 'Select Directory' button
        button_height = self.dir_button.sizeHint().height()
        self.dir_button.setFixedHeight(button_height)
        self.browse_button.setFixedHeight(button_height)
        self.refresh_button.setFixedHeight(button_height)
        self.run_button.setFixedHeight(button_height)
        self.language_button.setFixedHeight(button_height)

        # Place 'Run' and 'Switch to Ukrainian' buttons above 'Select Directory' and 'Refresh'
        left_button_layout = QHBoxLayout()
        left_button_layout.addWidget(self.run_button)
        left_button_layout.addWidget(self.language_button)

        # Directory selection, Browse, and Refresh button layout
        dir_button_layout = QHBoxLayout()
        dir_button_layout.addWidget(self.dir_button)
        dir_button_layout.addWidget(self.browse_button)
        dir_button_layout.addWidget(self.refresh_button)

        # File list widget
        self.file_list = QListWidget()
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Use QSizePolicy to control sizing
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable the horizontal scrollbar
        self.file_list.itemDoubleClicked.connect(self.open_file)  # Open file on double-click
        self.file_list.setDragEnabled(True)  # Enable drag from the left panel

        left_layout = QVBoxLayout()
        left_layout.addLayout(left_button_layout)  # Add 'Run' and 'Switch to Ukrainian' buttons at the top
        left_layout.addLayout(dir_button_layout)
        left_layout.addWidget(self.file_list)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Drag and drop area
        self.drop_label = QLabel('Drag and drop video files here\nOr click "Browse" to select')
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet(f"border: 2px dashed {DARK_THEME['border']}; padding: 20px; color: {DARK_THEME['text_color']};")
        self.drop_label.setAcceptDrops(True)
        self.setAcceptDrops(True)

        # Make the drag and drop area take up the full height of the window
        drop_layout = QVBoxLayout()
        drop_layout.addWidget(self.drop_label)

        center_widget = QWidget()
        center_widget.setLayout(drop_layout)
        splitter.addWidget(center_widget)

        # Set initial splitter ratios (left 10%, right 90%)
        splitter.setSizes([100, 700])

        # Final layout structure
        main_layout.addWidget(splitter)

        # Set the layout
        self.setLayout(main_layout)

        # Apply the initial theme (dark mode)
        self.apply_theme(DARK_THEME)

        # Store the selected video path
        self.selected_video = None
        self.selected_directory = None

    def create_custom_title_bar(self, layout):
        """Creates a custom title bar with dark color and a window logo."""
        title_bar = QHBoxLayout()

        # Icon
        icon_label = QLabel()
        logo_path = 'interfaces/images/icon.ico'
        if os.path.exists(logo_path):  # Ensure the logo exists
            icon_label.setPixmap(QPixmap(logo_path).scaled(24, 24, Qt.KeepAspectRatio))
        title_bar.addWidget(icon_label)

        # Title
        title_label = QLabel("Video Uploader")
        title_label.setStyleSheet(f"color: white;")  # Ensure 'Video Uploader' is always visible in white
        title_label.setFont(QFont("Helvetica", 11, QFont.DemiBold))
        title_bar.addWidget(title_label)
        title_bar.addStretch()

        # Dark/Light Mode Button (Sun and Moon Emojis) in the center
        self.theme_button = QPushButton("🌤 Light mode")
        self.theme_button.setFixedSize(150, 30)
        self.theme_button.setStyleSheet(f"background-color: {DARK_THEME['button_background']}; border-radius: 10px; color: {DARK_THEME['text_color']};")
        self.theme_button.clicked.connect(self.toggle_theme)

        title_bar.addStretch()  # Add space to center the button
        title_bar.addWidget(self.theme_button, 0, Qt.AlignCenter)
        title_bar.addStretch()  # Add space after the center button

        # Minimize button
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon('interfaces/images/minimize.png'))
        minimize_button.setIconSize(QSize(16, 16))
        minimize_button.setFixedSize(30, 30)
        minimize_button.setStyleSheet("border: none;")  # Remove unnecessary background styling
        minimize_button.clicked.connect(self.showMinimized)

        # Maximize/Restore button
        maximize_button = QPushButton()
        maximize_button.setIcon(QIcon('interfaces/images/maximize.png'))
        maximize_button.setIconSize(QSize(16, 16))
        maximize_button.setFixedSize(30, 30)
        maximize_button.setStyleSheet("border: none;")  # Remove unnecessary background styling
        maximize_button.clicked.connect(self.toggle_maximize_restore)

        # Close button
        close_button = QPushButton()
        close_button.setIcon(QIcon('interfaces/images/close.png'))
        close_button.setIconSize(QSize(16, 16))
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("border: none;")  # Remove unnecessary background styling
        close_button.clicked.connect(self.close)

        title_bar.addWidget(minimize_button)
        title_bar.addWidget(maximize_button)
        title_bar.addWidget(close_button)

        title_widget = QWidget()
        title_widget.setLayout(title_bar)
        title_widget.setStyleSheet(f"background-color: {DARK_THEME['background']};")
        title_widget.setFixedHeight(40)

        layout.addWidget(title_widget)

        # Enable dragging of the window by clicking the title bar
        title_widget.mousePressEvent = self.mousePressEvent
        title_widget.mouseMoveEvent = self.mouseMoveEvent

    def toggle_maximize_restore(self):
        """Toggles between maximize and restore."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def toggle_theme(self):
        """Toggles between dark and light themes."""
        if self.dark_mode:
            self.apply_theme(LIGHT_THEME)
            self.theme_button.setText("🌑 Dark mode")  # Change to moon icon and dark mode text
            self.theme_button.setStyleSheet(f"background-color: {LIGHT_THEME['button_background']}; color: {LIGHT_THEME['text_color']}; border-radius: 10px;")
        else:
            self.apply_theme(DARK_THEME)
            self.theme_button.setText("🌤 Light mode")  # Change to sun icon and light mode text
            self.theme_button.setStyleSheet(f"background-color: {DARK_THEME['button_background']}; color: {DARK_THEME['text_color']}; border-radius: 10px;")
        self.dark_mode = not self.dark_mode

    def mousePressEvent(self, event):
        """Start window drag on mouse press."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """Handle window dragging when the left mouse button is pressed."""
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def apply_theme(self, theme):
        """Applies the specified theme to the interface."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme['background']))
        palette.setColor(QPalette.WindowText, QColor(theme['text_color']))
        palette.setColor(QPalette.Button, QColor(theme['button_background']))
        palette.setColor(QPalette.ButtonText, QColor(theme['text_color']))
        palette.setColor(QPalette.Base, QColor(theme['background']))
        palette.setColor(QPalette.AlternateBase, QColor(theme['button_background']))
        palette.setColor(QPalette.Text, QColor(theme['text_color']))

        self.setPalette(palette)

        # Apply stylesheets to buttons and other widgets
        self.dir_button.setStyleSheet(f"background-color: {theme['button_background']}; color: {theme['text_color']}; border-radius: 10px;")
        self.refresh_button.setStyleSheet(f"background-color: {theme['button_background']}; color: {theme['text_color']}; border-radius: 10px;")
        self.browse_button.setStyleSheet(f"background-color: {theme['run_button_color']}; color: {theme['text_color']}; border-radius: 10px;")
        self.run_button.setStyleSheet(f"background-color: {theme['run_button_color']}; color: {theme['text_color']}; border-radius: 10px;")
        self.language_button.setStyleSheet(f"background-color: {theme['run_button_color']}; color: {theme['text_color']}; border-radius: 10px;")

        # Update the styles for drop area and file list using custom theme colors
        self.drop_label.setStyleSheet(f"border: 2px dashed {theme['border']}; padding: 20px; color: {theme['drop_label_text_color']}; background-color: {theme['background']};")
        self.file_list.setStyleSheet(f"background-color: {theme['background']}; color: {theme['file_list_text_color']}; border: 1px solid {theme['border']};")

        # Ensure the theme for the rest of the interface
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text_color']};")

    def select_directory(self):
        """Opens a file dialog to select a directory and lists its files."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selected_directory = directory
            self.refresh_directory()

    def refresh_directory(self):
        """Refreshes the file list in the selected directory."""
        if not self.selected_directory:
            return
        self.file_list.clear()
        files = os.listdir(self.selected_directory)
        for file in files:
            if not file.startswith('.'):  # Ignore hidden files
                self.file_list.addItem(file)

    def browse_file(self):
        """Opens a file dialog to select a video file."""
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv)")
        if video_path:
            self.selected_video = video_path
            self.drop_label.setText(f"Selected: {os.path.basename(video_path)}")

    def open_file(self, item):
        """Open file on double-click."""
        file_path = os.path.join(self.selected_directory, item.text())
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def dragEnterEvent(self, event):
        """Handles drag-and-drop for video files."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handles the drop event and sets the selected video."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.selected_video = files[0]
            self.drop_label.setText(f"Selected: {os.path.basename(self.selected_video)}")
            event.acceptProposedAction()

    def run_process(self):
        """Copies and renames the selected video to 'run_func_test'."""
        current_theme = DARK_THEME if self.dark_mode else LIGHT_THEME

        if not self.selected_video:
            msg = CustomMessageBox(
                title="No Video", 
                message="Please select a video before running.", 
                icon_type='warning',  # Use 'warning' icon
                current_theme=current_theme
            )
            msg.exec_()
            return

        if not self.selected_directory:
            msg = CustomMessageBox(
                title="No Directory", 
                message="Please select a directory first.", 
                icon_type='warning',  # Use 'warning' icon
                current_theme=current_theme
            )
            msg.exec_()
            return

        target_path = os.path.join(self.selected_directory, "run_func_test.mp4")
        try:
            shutil.copy(self.selected_video, target_path)
            msg = CustomMessageBox(
                title="Success", 
                message=f"Video copied and renamed to 'run_func_test.mp4' in {self.selected_directory}", 
                icon_type='info',  # Use 'info' icon
                current_theme=current_theme
            )
            msg.exec_()
        except Exception as e:
            msg = CustomMessageBox(
                title="Error", 
                message=f"Failed to copy the file: {e}", 
                icon_type='error',  # Use 'error' icon
                current_theme=current_theme
            )
            msg.exec_()

    def switch_language(self):
        """Switches between English and Ukrainian."""
        if self.language == 'EN':
            self.language = 'UA'
            self.dir_button.setText('Вибрати каталог')
            self.browse_button.setText('Огляд')
            self.run_button.setText('Запуск')
            self.drop_label.setText('Перетягніть відео сюди\nАбо натисніть "Огляд", щоб вибрати відео')
            self.language_button.setText('Переключитися на англійську')
        else:
            self.language = 'EN'
            self.dir_button.setText('Select Directory')
            self.browse_button.setText('Browse')
            self.run_button.setText('Run')
            self.drop_label.setText('Drag and drop video files here\nOr click "Browse" to select')
            self.language_button.setText('Switch to Ukrainian')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    uploader = VideoUploader()
    uploader.show()
    sys.exit(app.exec_())
