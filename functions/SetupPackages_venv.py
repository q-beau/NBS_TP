# -*- coding: utf-8 -*-
"""
Created on Wed Oct  1 11:12:38 2025

@author: u230231
"""

import os
import sys
import subprocess
import time

def install_packages_from_requirements(script_dir, requirements_file, python_exe=None):
    """
    Install packages using specified Python executable with robust fallback methods
    
    Parameters:
    - script_dir (str): Directory containing the requirements file
    - requirements_file (str): Path to requirements file
    - python_exe (str): Python executable to use (default: sys.executable)
    
    Returns:
    - bool: True if installation successful, False otherwise
    """
    if python_exe is None:
        python_exe = sys.executable
    
    print(f"📦 Installing packages using: {python_exe}")
    print(f"📋 From requirements: {requirements_file}")
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    # Multiple installation strategies for maximum compatibility
    install_strategies = [
        {
            "name": "Standard installation",
            "command": [python_exe, "-m", "pip", "install", "-r", requirements_file]
        },
        {
            "name": "With trusted hosts (corporate networks)",
            "command": [python_exe, "-m", "pip", "install", "-r", requirements_file,
                       "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org"]
        },
        {
            "name": "With upgrade flag",
            "command": [python_exe, "-m", "pip", "install", "-r", requirements_file, "--upgrade"]
        },
        {
            "name": "User installation",
            "command": [python_exe, "-m", "pip", "install", "-r", requirements_file, "--user"]
        },
        {
            "name": "Force reinstall",
            "command": [python_exe, "-m", "pip", "install", "-r", requirements_file, 
                       "--force-reinstall", "--no-deps"]
        }
    ]
    
    # First, ensure pip is up to date
    try:
        print("⬆️ Upgrading pip...")
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], 
                      capture_output=True, text=True, timeout=120)
    except:
        print("⚠️ Could not upgrade pip, continuing...")
    
    # Try each installation strategy
    for i, strategy in enumerate(install_strategies, 1):
        try:
            print(f"🔧 Trying {strategy['name']} (method {i}/{len(install_strategies)})...")
            
            result = subprocess.run(
                strategy["command"],
                capture_output=True,
                text=True,
                cwd=script_dir,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Success with {strategy['name']}!")
                return True
            else:
                print(f"❌ Failed: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Method {i} timed out, trying next...")
        except Exception as e:
            print(f"❌ Method {i} error: {str(e)[:100]}...")
    
    # Final fallback: install packages individually
    print("🔄 Trying individual package installation as final fallback...")
    return install_packages_individually(python_exe, requirements_file, script_dir)

def install_packages_individually(python_exe, requirements_file, script_dir):
    """
    Fallback method: install each package individually
    """
    try:
        with open(requirements_file, 'r') as f:
            packages = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)
        
        if not packages:
            print("📝 No packages found in requirements file")
            return True
        
        success_count = 0
        total_packages = len(packages)
        
        print(f"📦 Installing {total_packages} packages individually...")
        
        for i, package in enumerate(packages, 1):
            try:
                print(f"   Installing {package} ({i}/{total_packages})...")
                result = subprocess.run([
                    python_exe, "-m", "pip", "install", package
                ], capture_output=True, text=True, timeout=180, cwd=script_dir)
                
                if result.returncode == 0:
                    success_count += 1
                    print(f"   ✅ {package}")
                else:
                    print(f"   ❌ Failed: {package}")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Timeout: {package}")
            except Exception as e:
                print(f"   ❌ Error: {package} - {str(e)[:50]}...")
        
        print(f"📊 Successfully installed {success_count}/{total_packages} packages")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Individual installation failed: {e}")
        return False

def check_installed_packages(script_dir, requirements_file='requirements.txt', python_exe=None):
    """
    Check if packages from requirements file are properly installed
    
    Parameters:
    - script_dir (str): Directory where the requirements file is located
    - requirements_file (str): Name of the requirements file (default: 'requirements.txt')
    - python_exe (str): Python executable to use for testing (default: sys.executable)
    
    Returns:
    - bool: True if all packages are working, False otherwise
    """
    if python_exe is None:
        python_exe = sys.executable
    
    # Handle both full path and filename
    if os.path.isabs(requirements_file):
        requirements_path = requirements_file
    else:
        requirements_path = os.path.join(script_dir, requirements_file)
    
    if not os.path.exists(requirements_path):
        print(f"❌ {requirements_file} not found in {script_dir}")
        return False
    
    # Extract package names from requirements
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read().strip().split('\n')
            
        package_names = []
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                # Handle different version specifiers (>=, ==, ~=, >, <, !=)
                for separator in ['>=', '==', '~=', '>', '<', '!=']:
                    if separator in req:
                        req = req.split(separator)[0]
                        break
                # Handle extras (like package[extra])
                if '[' in req:
                    req = req.split('[')[0]
                package_names.append(req.strip())
                
    except Exception as e:
        print(f"❌ Error reading requirements file: {e}")
        return False
    
    if not package_names:
        print("📝 No packages found to test")
        return True
    
    print(f"\n🧪 Testing package imports using: {python_exe}")
    print(f"📋 From: {requirements_path}")
    
    # Test imports by running Python subprocess to avoid affecting current session
    all_working = True
    failed_packages = []
    
    for package in package_names:
        try:
            # Create a simple import test script
            test_script = f"""
import sys
try:
    import {package}
    print("SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"OTHER_ERROR: {{e}}")
    sys.exit(1)
"""
            
            # Run the test in the specified Python environment
            result = subprocess.run([
                python_exe, "-c", test_script
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package}: {result.stdout.strip() or result.stderr.strip()}")
                all_working = False
                failed_packages.append(package)
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {package}: Import test timed out")
            all_working = False
            failed_packages.append(package)
        except Exception as e:
            print(f"  ❌ {package}: Test error - {str(e)[:50]}")
            all_working = False
            failed_packages.append(package)
    
    if not all_working:
        print(f"\n⚠️ Failed packages: {', '.join(failed_packages)}")
        print("💡 Try running the installation again or check for package name issues")
    
    return all_working

def create_requirements_backup(script_dir, requirements_file):
    """
    Create a backup of requirements.txt with current installed versions
    """
    try:
        backup_file = os.path.join(script_dir, f"requirements_backup_{int(time.time())}.txt")
        result = subprocess.run([
            sys.executable, "-m", "pip", "freeze"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(backup_file, 'w') as f:
                f.write(result.stdout)
            print(f"📋 Created requirements backup: {backup_file}")
        
    except Exception as e:
        print(f"⚠️ Could not create backup: {e}")
