#!/usr/bin/env python
"""
Run the Enhanced Streamlit app using Python directly
Execute with: python run.py
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Set multiprocessing start method for Windows compatibility
    if sys.platform == "win32":
        os.environ["PYTHONUNBUFFERED"] = "1"
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app_enhanced.py"],
            check=False
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("Streamlit app interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
