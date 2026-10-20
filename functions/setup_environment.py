# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 14:27:06 2026

@author: qbeau
"""
import sys
import os
import glob
import subprocess
import urllib.request


def setup_environment(script_dir, env_name="NbS_TP", r_version="4.5.1",
                      required_packages=("numpy", "pandas", "matplotlib")):
    """Verify the environment, check project structure, clean old outputs
    and ensure a local R installation is available.

    Parameters
    ----------
    script_dir : str
        Directory containing main.py (project root).
    env_name : str
        String that must appear in the Python executable path.
    r_version : str
        R version to install if no local installation is found.
    required_packages : iterable of str
        Python packages that must be importable.

    Returns
    -------
    data_path, results_path, functions_dir, Rscript_exe : str
    """
    line = "=" * 50
    print("CELL 1: ENVIRONMENT SETUP")
    print(line)

    # 1. Python environment
    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {sys.version.split()[0]}")
    if env_name not in sys.executable:
        raise EnvironmentError(
            f"Wrong environment: '{env_name}' not found in the Python path. "
            "Select the interpreter of the course environment in Spyder "
            "(Tools > Preferences > Python interpreter) and restart the kernel.")
    print(f"Environment check : OK ({env_name})")

    # 2. Project paths
    data_path = os.path.join(script_dir, "data")
    results_path = os.path.join(script_dir, "results")
    functions_dir = os.path.join(script_dir, "functions")

    os.chdir(script_dir)
    if functions_dir not in sys.path:
        sys.path.insert(0, functions_dir)

    print("\nProject paths")
    print(f"  Working directory   : {script_dir}")
    print(f"  Data directory      : {data_path}")
    print(f"  Results directory   : {results_path}")
    print(f"  Functions directory : {functions_dir}")

    for name, path in (("data", data_path), ("results", results_path),
                       ("functions", functions_dir)):
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Required folder missing: '{name}' ({path})")
        print(f"  Folder '{name}': found")

    # 3. Required packages
    print("\nChecking required packages")
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}: OK")
        except ImportError:
            print(f"  {package}: MISSING")
            missing.append(package)
    if missing:
        raise ImportError(
            f"Missing packages: {', '.join(missing)}. "
            f"Run in Anaconda Prompt: conda install {' '.join(missing)}")

    # 4. Remove outputs from previous runs
    print("\nCleaning previous results")
    files_removed = 0
    for pattern in (os.path.join(data_path, "DataRothCRun_*.csv"),
                    os.path.join(results_path, "*.csv")):
        for f in glob.glob(pattern):
            try:
                os.remove(f)
                files_removed += 1
            except OSError as e:
                print(f"  Warning: could not remove {f} ({e})")
    if files_removed:
        print(f"  Removed {files_removed} old result file(s)")
    else:
        print("  No old results to clean")

    # 5. Local R installation
    print("\nChecking R installation")
    install_dir = os.path.join(script_dir, "rothc", "R")
    Rscript_exe = os.path.join(install_dir, "bin", "x64", "Rscript.exe")
    installer_path = os.path.join(script_dir, "R-installer.exe")
    r_url = ("https://cran.r-project.org/bin/windows/base/old/"
             f"{r_version}/R-{r_version}-win.exe")

    if os.path.exists(Rscript_exe):
        print(f"  R {r_version} already installed, skipping installation")
    else:
        if not os.path.exists(installer_path):
            print(f"  Downloading R {r_version} installer")
            try:
                urllib.request.urlretrieve(r_url, installer_path)
                print("  Download complete")
            except Exception as e:
                raise RuntimeError(
                    f"R download failed ({e}). Download R {r_version} manually "
                    "from https://cran.r-project.org/bin/windows/base/old/ "
                    f"and save it as {installer_path}")
        os.makedirs(install_dir, exist_ok=True)
        print(f"  Installing R silently into {install_dir}")
        subprocess.run([installer_path, "/VERYSILENT", f"/DIR={install_dir}",
                        "/NORESTART"], check=True)
        print("  R installation complete")
    print(f"  Rscript : {Rscript_exe}")

    print("\n" + line)
    print("SETUP COMPLETE - Ready for Cell 2")
    print(line)

    return data_path, results_path, functions_dir, Rscript_exe

