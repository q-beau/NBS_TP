# -*- coding: utf-8 -*-
"""
Created on Wed Oct  1 11:08:16 2025

@author: u230231
"""
import os 
import sys
def check_running_in_venv(script_dir):
    """
    Check if we're already running in the local virtual environment
    """
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        # Check if it's our local venv
        expected_venv = os.path.join(script_dir, "venv")
        current_prefix = sys.prefix
        
        # Normalize paths for comparison
        expected_venv = os.path.normpath(expected_venv)
        current_prefix = os.path.normpath(current_prefix)
        
        if expected_venv == current_prefix:
            print("✅ Already running in local virtual environment")
            return True, sys.executable, None
        else:
            print(f"⚠️ Running in different venv: {current_prefix}")
            print(f"   Expected: {expected_venv}")
    else:
        print("ℹ️ Not running in virtual environment")
    
    return False, None, None