#!/usr/bin/env python3

import sys
import os

# Add the current directory to the Python path so we can import the GUI module
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the GUI
from media_organizer_gui import main

if __name__ == "__main__":
    main()