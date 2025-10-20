#!/usr/bin/env python3
"""
Simple launcher for the Media Organizer GUI.
Launches the GUI from the src/ folder.
"""

import sys
import os

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
sys.path.insert(0, src_dir)

# Import and run the GUI
from media_organizer_gui import main

if __name__ == "__main__":
    main()
