#!/usr/bin/env python
"""
Run the Enhanced Streamlit app using Python directly
Execute with: python run.py
"""

import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app_enhanced.py"])
