from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from aqt.theme import theme_manager
from datetime import datetime
import json
import os

# Import config dialog
try:
    from .config_dialog import show_config_dialog
except ImportError:
    # Fallback for direct import
    try:
        from config_dialog import show_config_dialog
    except ImportError:
        show_config_dialog = None

class ReviewHistoryPopup(QWidget):
    def __init__(self):
        super().__init__(mw)  # Set parent to main window
        self.config = mw.addonManager.getConfig(__name__)
        
        # Don't use WindowStaysOnTopHint - just make it a child widget
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(self.layout)
        
        self.text_label = QLabel()
        self.text_label.setTextFormat(Qt.TextFormat.RichText)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.update_styling()
        self.layout.addWidget(self.text_label)
        
    def update_styling(self):
        # Get Anki's current zoom level
        zoom_factor = mw.reviewer.web.zoomFactor() if mw.reviewer and mw.reviewer.web else 1.0
        # Apply a dampened zoom - only 40% of the actual zoom effect
        dampened_zoom = 1.0 + (zoom_factor - 1.0) * 0.4
        # Base font size is 12px, adjusted by dampened zoom
        font_size = int(12 * dampened_zoom)
        
        # Get Anki's theme colors with transparency
        if theme_manager.night_mode:
            bg_color = "rgba(39, 40, 40, 0.85)"  # Semi-transparent dark
            text_color = "#ffffff"
            border_color = "rgba(58, 58, 58, 0.8)"
            relearn_color = "#ff8589"
            review_color = "#7cb342"
            learn_color = "#2196f3"
            date_color = "#bbbbbb"
        else:
            bg_color = "rgba(255, 255, 255, 0.85)"  # Semi-transparent light
            text_color = "#000000"
            border_color = "rgba(221, 221, 221, 0.8)"
            relearn_color = "#c33"
            review_color = "#0a0"
            learn_color = "#00a"
            date_color = "#555555"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        self.text_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 8px 12px;
                font-family: monospace;
                font-size: {font_size}px;
            }}
        """)
        
        # Store colors for use in update_history
        self.colors = {
            'relearn': relearn_color,
            'review': review_color,
            'learn': learn_color,
            'date': date_color,
            'text': text_color,
            'rating_1': relearn_color  # Rating 1 uses same red as relearn
        }
        
    def update_history(self, card):
        if not card:
            self.hide()
            return
        
        # Check if window is small to determine how many lines to show
        mw_geo = mw.geometry()
        screen_geo = QApplication.primaryScreen().geometry()
        is_small = mw_geo.width() <= screen_geo.width() * 0.5
        
        # Get review log - limit to 1 line if small window
        max_lines = 1 if is_small else self.config.get("max_lines", 10)
        
        revlog = mw.col.db.all(
            "select id, ease, ivl, type from revlog where cid = ? order by id desc limit ?",
            card.id,
            max_lines
        )
        
        if not revlog:
            self.text_label.setText(f'<span style="color: {self.colors["text"]}">No review history</span>')
        else:
            lines = []
            ease_map = {1: "1", 2: "2", 3: "3", 4: "4"}
            type_map = {0: "Learn", 1: "Review", 2: "Relearn", 3: "Cram"}
            
            for log_id, ease, ivl, log_type in revlog:
                # Convert timestamp (milliseconds) to readable date
                timestamp = log_id / 1000
                date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d @ %H:%M")
                ease_str = ease_map.get(ease, str(ease))
                type_str = type_map.get(log_type, str(log_type))
                
                # Format interval
                if ivl < 0:
                    ivl_str = f"{-ivl // 60}m" if -ivl >= 60 else f"{-ivl}s"
                elif ivl == 0:
                    ivl_str = "0d"
                else:
                    ivl_str = f"{ivl}d" if ivl < 365 else f"{ivl // 365}y"
                
                # Color code the type
                if log_type == 2:  # Relearn
                    type_color = self.colors['relearn']
                elif log_type == 1:  # Review
                    type_color = self.colors['review']
                else:  # Learn
                    type_color = self.colors['learn']
                
                date_color = self.colors['date']
                text_color = self.colors['text']
                
                # Color rating 1 red like in the standard info window
                rating_color = self.colors['rating_1'] if ease == 1 else text_color
                
                # Build HTML line with proper spacing
                line = '<span>'
                line += f'<span style="color: {date_color}">{date_str}</span> '
                line += f'<span style="color: {type_color}">{type_str:7}</span> '
                line += f'<span style="color: {rating_color}">{ease_str:1}</span> '
                line += f'<span style="color: {text_color}">{ivl_str:>10}</span>'
                line += '</span>'
                
                lines.append(line)
            
            # --- THE FIX FOR ORDERING ---
            # If "Newest at Bottom" is True, we reverse the list 
            # (since SQL query returns Newest-First)
            if self.config.get("newest_at_bottom", True):
                lines.reverse()
            
            self.text_label.setText("<br>".join(lines))
        
        self.adjustSize()
        self.position_popup()
        
        # If small window, inject CSS to bump card content down
        if is_small and mw.reviewer and mw.reviewer.web:
            popup_height = self.height()
            mw.reviewer.web.eval(f"""
                (function() {{
                    let style = document.getElementById('killfeed-margin');
                    if (!style) {{
                        style = document.createElement('style');
                        style.id = 'killfeed-margin';
                        document.head.appendChild(style);
                    }}
                    style.textContent = '#qa {{ margin-top: {popup_height + 10}px !important; }}';
                }})();
            """)
        elif mw.reviewer and mw.reviewer.web:
            # Remove the margin if not in small mode
            mw.reviewer.web.eval("""
                (function() {
                    let style = document.getElementById('killfeed-margin');
                    if (style) style.remove();
                })();
            """)
        
        self.show()
        
    def position_popup(self):
        if not mw.reviewer or not mw.reviewer.web:
            return
            
        corner = self.config.get("corner", "top-right")
        
        # Get main window geometry
        main_window = mw
        mw_geo = main_window.geometry()
        screen_geo = QApplication.primaryScreen().geometry()
        
        # Check if window is 50% or less of screen width
        is_small = mw_geo.width() <= screen_geo.width() * 0.5
        
        popup_width = self.width()
        popup_height = self.height()
        
        # Get the reviewer web view position to align properly
        reviewer_y_offset = 70  # Approximate height of title bar + toolbar
        
        if is_small:
            # Center above the card display
            x = mw_geo.x() + (mw_geo.width() - popup_width) // 2
            y = mw_geo.y() + reviewer_y_offset
        else:
            # Position in corner - aligned with card display area
            if corner == "top-left":
                x = mw_geo.x() + 10
                y = mw_geo.y() + reviewer_y_offset
            elif corner == "top-right":
                x = mw_geo.x() + mw_geo.width() - popup_width - 10
                y = mw_geo.y() + reviewer_y_offset
            elif corner == "bottom-left":
                x = mw_geo.x() + 10
                y = mw_geo.y() + mw_geo.height() - popup_height - 50
            else:  # bottom-right
                x = mw_geo.x() + mw_geo.width() - popup_width - 10
                y = mw_geo.y() + mw_geo.height() - popup_height - 50
        
        self.move(x, y)

# Global popup instance
popup = None

def on_reviewer_did_show_question(card):
    global popup
    if popup is None:
        popup = ReviewHistoryPopup()
    else:
        # Update styling in case theme changed
        popup.update_styling()
    popup.update_history(card)
    # Always reposition when showing a new card
    popup.position_popup()

def on_reviewer_will_end():
    global popup
    if popup:
        popup.hide()

# Setup hooks
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_question)
gui_hooks.reviewer_will_end.append(on_reviewer_will_end)

# Cleanup on profile unload
def cleanup():
    global popup
    if popup:
        popup.close()
        popup = None

gui_hooks.profile_will_close.append(cleanup)

# Add menu item for configuration
def setup_menu():
    if show_config_dialog:
        action = QAction("Card History Killfeed Config...", mw)
        action.triggered.connect(show_config_dialog)
        mw.form.menuTools.addAction(action)

gui_hooks.main_window_did_init.append(setup_menu)