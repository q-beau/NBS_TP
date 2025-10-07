import subprocess
import sys
import importlib.util
import os

def is_package_installed(package_name):
    """
    Check if a package is installed and importable
    """
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False

def get_package_name_from_requirement(requirement):
    """
    Extract package name from requirement string (e.g., 'pandas>=2.0.0' -> 'pandas')
    """
    requirement = requirement.strip()
    if not requirement or requirement.startswith('#'):
        return None
    
    # Remove version specifiers
    for separator in ['>=', '==', '~=', '>', '<', '!=', '[']:
        if separator in requirement:
            requirement = requirement.split(separator)[0]
            break
    
    return requirement.strip()

def read_requirements(requirements_file):
    """
    Read and parse requirements.txt file
    """
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return []
    
    try:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        
        requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        
        return requirements
        
    except Exception as e:
        print(f"❌ Error reading requirements file: {e}")
        return []

def install_missing_packages(script_dir, requirements_file='requirements.txt'):
    """
    Check for missing packages and install them in current environment
    
    Parameters:
    - script_dir (str): Directory containing requirements file
    - requirements_file (str): Requirements file name or path
    
    Returns:
    - bool: True if all packages are available, False otherwise
    """
    # Handle both filename and full path
    if os.path.isabs(requirements_file):
        req_path = requirements_file
    else:
        req_path = os.path.join(script_dir, requirements_file)
    
    print(f"📋 Checking packages from: {req_path}")
    print(f"🐍 Using Python: {sys.executable}")
    
    # Read requirements
    requirements = read_requirements(req_path)
    if not requirements:
        print("ℹ️ No requirements found")
        return True
    
    # Check which packages are missing
    missing_packages = []
    installed_packages = []
    
    print("\n🔍 Checking installed packages...")
    
    for requirement in requirements:
        package_name = get_package_name_from_requirement(requirement)
        if package_name:
            if is_package_installed(package_name):
                print(f"  ✅ {package_name}")
                installed_packages.append(package_name)
            else:
                print(f"  ❌ {package_name} - Missing")
                missing_packages.append(requirement)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        
        success_count = 0
        for requirement in missing_packages:
            try:
                print(f"   Installing {requirement}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", requirement, 
                    "--upgrade-strategy", "only-if-needed"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"   ✅ {requirement}")
                    success_count += 1
                else:
                    print(f"   ❌ {requirement}: {result.stderr[:100]}...")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏰ {requirement}: Installation timeout")
            except Exception as e:
                print(f"   ❌ {requirement}: Error - {str(e)[:50]}")
        
        print(f"\n📊 Installation summary: {success_count}/{len(missing_packages)} packages installed")
        
        # Verify installations
        print("\n🧪 Verifying installations...")
        all_good = True
        for requirement in missing_packages:
            package_name = get_package_name_from_requirement(requirement)
            if package_name and is_package_installed(package_name):
                print(f"  ✅ {package_name}")
            else:
                print(f"  ❌ {package_name}: Still missing")
                all_good = False
        
        return all_good
    
    else:
        print("\n🎉 All required packages are already installed!")
        return True

# Main function for your script
def check_and_install_packages_safe(script_dir, requirements_file='requirements.txt', python_exe=None):
    """
    Simple package installer for educational use
    Just checks and installs missing packages in current environment
    """
    return install_missing_packages(script_dir, requirements_file)
