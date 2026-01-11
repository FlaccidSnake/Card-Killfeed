# -*- coding: utf-8 -*-
"""
Card History Killfeed
Main entry point for the addon
"""

from . import card_history_killfeed
from . import config_dialog
from aqt import mw

# Register config dialog with Anki's addon manager
mw.addonManager.setConfigAction(__name__, config_dialog.show_config_dialog)