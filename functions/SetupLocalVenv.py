import os
import sys
import subprocess
import platform

def setup_local_venv(script_dir):
    """
    Create and use a local virtual environment for maximum portability
    """
    print("🔧 Setting up local virtual environment...")
    
    # Define venv path in script directory
    venv_path = os.path.join(script_dir, "venv")
    
    # Check if venv already exists
    venv_exists = os.path.exists(venv_path)
    
    if venv_exists:
        # Check if it's a valid venv by looking for pyvenv.cfg
        pyvenv_cfg = os.path.join(venv_path, "pyvenv.cfg")
        if os.path.exists(pyvenv_cfg):
            print(f"✅ Found existing virtual environment: {venv_path}")
        else:
            print(f"⚠️ Invalid venv found, recreating...")
            import shutil
            shutil.rmtree(venv_path)
            venv_exists = False
    
    # Create venv if it doesn't exist
    if not venv_exists:
        print("📦 Creating new virtual environment...")
        try:
            # Use --copies for true portability (no symlinks)
            subprocess.run([
                sys.executable, "-m", "venv", venv_path, "--copies"
            ], check=True, capture_output=True, text=True)
            print(f"✅ Virtual environment created: {venv_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create venv: {e}")
            return None, None
        except FileNotFoundError:
            print("❌ Python venv module not available")
            return None, None
    
    # Get the correct Python and pip executables from venv
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_path, "bin", "python")
        venv_pip = os.path.join(venv_path, "bin", "pip")
    
    # Verify the executables exist
    if not os.path.exists(venv_python):
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return None, None
    
    print(f"🐍 Using Python: {venv_python}")
    return venv_python, venv_pip