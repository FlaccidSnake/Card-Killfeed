# -*- coding: utf-8 -*-
"""
Card History Killfeed Config Dialog
"""
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QFrame, QGroupBox
from aqt import mw
from aqt.utils import tooltip


class KillfeedConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        config = mw.addonManager.getConfig(__name__)
        
        # Handle missing config gracefully
        if config is None:
            config = {
                "corner": "top-right",
                "max_lines": 10
            }
        
        self.corner = config.get("corner", "top-right")
        self.max_lines = config.get("max_lines", 10)
        
        self.setWindowTitle("Card History Killfeed Configuration")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        
        # Position Settings
        position_group = QGroupBox("Position")
        position_layout = QVBoxLayout()
        
        # Corner selection
        corner_layout = QHBoxLayout()
        corner_label = QLabel("Popup corner position:")
        self.corner_combo = QComboBox()
        self.corner_combo.addItems([
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right"
        ])
        self.corner_combo.setCurrentText(self.corner)
        corner_layout.addWidget(corner_label)
        corner_layout.addWidget(self.corner_combo)
        corner_layout.addStretch()
        position_layout.addLayout(corner_layout)
        
        corner_info = QLabel(
            "<i>Position applies when window is larger than 50% of screen width</i>"
        )
        corner_info.setWordWrap(True)
        position_layout.addWidget(corner_info)
        
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Display Settings
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout()
        
        # Max lines selection
        lines_layout = QHBoxLayout()
        lines_label = QLabel("Maximum lines to display:")
        self.lines_spinbox = QSpinBox()
        self.lines_spinbox.setMinimum(1)
        self.lines_spinbox.setMaximum(100)
        self.lines_spinbox.setValue(self.max_lines)
        lines_layout.addWidget(lines_label)
        lines_layout.addWidget(self.lines_spinbox)
        lines_layout.addStretch()
        display_layout.addLayout(lines_layout)
        
        lines_info = QLabel(
            "<i>When window is 50% or less of screen width, only 1 line is shown</i>"
        )
        lines_info.setWordWrap(True)
        display_layout.addWidget(lines_info)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_config(self):
        """Save configuration"""
        config = mw.addonManager.getConfig(__name__)
        
        # Create new config if it doesn't exist
        if config is None:
            config = {}
        
        config["corner"] = self.corner_combo.currentText()
        config["max_lines"] = self.lines_spinbox.value()
        
        mw.addonManager.writeConfig(__name__, config)
        
        tooltip("Configuration saved! Changes will apply to the next card.")
        self.accept()


def show_config_dialog():
    """Show the configuration dialog"""
    dialog = KillfeedConfigDialog(mw)
    dialog.exec()