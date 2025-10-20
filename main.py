# -*- coding: utf-8 -*-
"""
Nature-Based Solutions for Climate Change Mitigation
=====================================================

Practical Session: Soil Organic Carbon Modeling with RothC
-----------------------------------------------------------

Created on Thu Sep 18 10:15:38 2025

@author: qbeau
"""

#!/usr/bin/env python3

#%% Cell 1: Environment Setup and Verification


print("🔧 CELL 1: ENVIRONMENT SETUP")
print("=" * 50)

import sys, os, glob
import subprocess
import urllib.request

# Check if in correct environment
print(f"🐍 Using Python: {sys.executable}")
print(f"🐍 Python version: {sys.version.split()[0]}")

if 'NbS_TP' not in sys.executable:
    print("\n⚠️ WARNING: You may not be in the correct conda environment!")
    print("\n❌ Stopping execution - please activate NBS_TP environment first")
    raise EnvironmentError("Wrong conda environment - NBS_TP required")
else:
    print("✅ Correct environment: NBS_TP")

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, 'data')
results_path = os.path.join(script_dir, 'results')
functions_dir = os.path.join(script_dir, "functions")

# Add functions directory to path
sys.path.insert(0, functions_dir)

print(f"\n📁 Working directory: {script_dir}")
print(f"📁 Data directory: {data_path}")
print(f"📁 Results directory: {results_path}")
print(f"📁 Functions directory: {functions_dir}")

# Verify required directories exist
for path_name, path in [("data", data_path), ("results", results_path), ("functions", functions_dir)]:
    if not os.path.exists(path):
        print(f"❌ ERROR: {path_name} folder not found at {path}")
        raise FileNotFoundError(f"Required folder missing: {path_name}")
    else:
        print(f"✅ {path_name.capitalize()} folder found")

# Verify critical packages are installed
print("\n📦 Verifying required packages...")
required_packages = ['numpy', 'pandas', 'matplotlib']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - MISSING")
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠️ WARNING: Missing packages: {', '.join(missing_packages)}")
    print("💡 Run in Anaconda Prompt:")
    print(f"   conda activate NBS_TP")
    print(f"   conda install {' '.join(missing_packages)}")
    raise ImportError(f"Missing required packages: {missing_packages}")

# Clear previous results
print("\n🧹 Cleaning previous results...")
files_removed = 0

for pattern in ["DataRothCRun_*.csv"]:
    for f in glob.glob(os.path.join(data_path, pattern)):
        try:
            os.remove(f)
            files_removed += 1
        except Exception as e:
            print(f"⚠️ Could not remove {f}: {e}")

for f in glob.glob(os.path.join(results_path, "*.csv")):
    try:
        os.remove(f)
        files_removed += 1
    except Exception as e:
        print(f"⚠️ Could not remove {f}: {e}")

if files_removed > 0:
    print(f"✅ Removed {files_removed} old result file(s)")
else:
    print("✅ No old results to clean")

print("\n" + "=" * 50)
print("🎉 SETUP COMPLETE - Ready for Cell 2!")
print("=" * 50)

#------------------ R installation ---------------------------------------#

# URL for R installer - using the latest version link
r_installer_url = "https://cran.r-project.org/bin/windows/base/R-4.5.1-win.exe"
installer_path = "R-installer.exe"

# Download installer if it is not present
if not os.path.exists(installer_path):
    print("Downloading R installer...")
    try:
        urllib.request.urlretrieve(r_installer_url, installer_path)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading: {e}")
        print("Please download R manually from: https://cran.r-project.org/bin/windows/base/")

# Target installation directory
install_dir = os.path.join(script_dir, "rothc","R")
# Ensure the folder exists
os.makedirs(install_dir, exist_ok=True)

# Prepare silent install command with custom target folder
silent_install_cmd = [
    installer_path,
    "/VERYSILENT",
    f"/DIR={install_dir}",
    "/NORESTART"
]

print(f"Installing R silently into {install_dir} ...")
subprocess.run(silent_install_cmd, check=True)
print("R installation done.")

# Set Rscript path for later use
Rscript_exe = os.path.join(install_dir, "bin", "x64", "Rscript.exe")
print(f"Rscript.exe is located at: {Rscript_exe}")


# %% Cell 2: Build RothC scenarios from the baseline

print("🔧 CELL 2: LAUNCH ROTHC")
print("=" * 50)

import numpy as np
import pandas as pd
import os
import glob
import subprocess
import matplotlib.pyplot as plt
from itertools import combinations
import configparser


#------------------ Script variables ---------------------------------------#
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'param.ini'))
#Rpath
# Rpath = config['Paths']['Rpath']
#Warming scenarios
warming_scenarios = config['Scenarios']['warming_scenarios'].split(',')
#Straw return percentage
straw_scenarios = list(map(int, config['Scenarios']['straw_scenarios'].split(',')))
#Rotation scenario
rotation_scenarios = config['Scenarios']['rotation_scenarios'].split(',')

#List of available rotations in param.ini : ecofoodref, ecofoodvegan, baselinesubset
#List of available warming scenarios in param.ini : 8.5,4.5,2.6
#List of available straw scenarios in param.ini : 0,10,20,... (between 0 and 100) 
#------------------ Generate input files for RothC --------------------------------------#

from CreateRothCDataIn import CreateRothCDataIn

# Triple loop: iterate through all scenario combinations
for i in range(len(warming_scenarios)):
    warming_scenario = warming_scenarios[i]
    
    for j in range(len(straw_scenarios)):
        straw_scenario = straw_scenarios[j]
        
        for k in range(len(rotation_scenarios)):
            rotation_scenario = rotation_scenarios[k]
            
            # Create the RothC input data file for this combination
            DataRothCIn, yield_table = CreateRothCDataIn(data_path, warming_scenario, 
                                           straw_scenario, rotation_scenario)
            
            # Add scenario identifier to the dataframe
            DataRothCIn['Scenario'] = warming_scenario + '_' + rotation_scenario + '_' + str(straw_scenario)
            
            # Save as CSV for RothC to read
            DataRothCIn.to_csv(os.path.join(script_dir, 'data','DataRothCRun.csv'), index=False)
            
            # Setup R environment
            RscriptFileName = os.path.join(script_dir, 'rothc', 'rothc_MC.R')
            
            # Run RothC in R
            try:
                result = subprocess.run([Rscript_exe, RscriptFileName], check=True)
                print(f"  ✅ RothC R script executed successfully for {DataRothCIn['Scenario'].iloc[0]}")
                print("   STDOUT:\n", result.stdout)
                if result.stderr:
                    print("   STDERR:\n", result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"  ❌ RothC R script failed for {DataRothCIn['Scenario'].iloc[0]}")
                print("   STDOUT:\n", e.stdout)
                print("   STDERR:\n", e.stderr)


# %% Cell 3: Load and visualize the results

print("🔧 CELL 3: PLOT RESULTS")
print("=" * 50)

%matplotlib qt

# Load the result files from RothC
results_dir = os.path.join(script_dir, "results")

# Select the csv files: either all, or select a specific combination
SelectCrit = 'All'  # either 'All', 'WS', 'ST', 'WS+ST','WS+ROT'

#Sets visibility of uncertainty curves
ShowUncertainty = True 

if SelectCrit == 'All':
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
elif SelectCrit == 'WS+ST':
    SelectWS = '2.6'
    SelectST = '15'
    csv_files = glob.glob(os.path.join(results_dir, f"*{SelectWS}*{SelectST}*.csv"))
elif SelectCrit == 'WS+ROT':
    SelectWS = '2.6'
    SelectROT = 'ecofoodref'
    csv_files = glob.glob(os.path.join(results_dir, f"*{SelectWS}*{SelectROT}*.csv"))

all_results = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f) for f in csv_files}

#Fitler over the reporting period
rp = 16 #reporting period in years
all_results_sliced = {key: df.iloc[0:rp*12] for key, df in all_results.items()}


# PLOT AND ANALYZE THE RESULTS 
# -----------------------------
# Plot 1: SOC time series overlayed
# -----------------------------

# Define colors for different WS
color_values = ['#a1afde', '#fbc464', '#954130']  # same length as warming_scenarios
colors = {scenario: color for scenario, color in zip(warming_scenarios, color_values)}

# Define line styles for different ROT
line_symbols = ['-.', '-', ':']  # same length as rotation_scenarios
plot_styles = {scenario: style for scenario, style in zip(rotation_scenarios, line_symbols)}

# Define hatch patterns for different SR
hatch_symbols = ['-', '+', '']  # same length as straw_scenarios
hatch_styles = {str(scenario): hatch for scenario, hatch in zip(straw_scenarios, hatch_symbols)}


# Add a general legend with all possible entries for hatch, color and linestyle
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

legend_elements = []

# Add color legend (WS scenarios)
for ws, color in colors.items():
    legend_elements.append(Line2D([0], [0], color=color, lw=3, label=f'WS {ws}'))

# Add line style legend (ROT scenarios)
for rot, style in plot_styles.items():
    legend_elements.append(Line2D([0], [0], color='black', lw=2, linestyle=style, label=f'{rot}'))

# Add hatch legend (SR scenarios)
for sr, hatch in hatch_styles.items():
    if hatch:  # Only add non-empty hatches
        legend_elements.append(Patch(facecolor='none', hatch=hatch*3, 
                                    edgecolor='black', linewidth=1, label=f'SR {sr}'))
    else:
        legend_elements.append(Patch(facecolor='lightgray', label=f'SR {sr}'))

plt.close('all')
fig, ax = plt.subplots(figsize=(10, 6))


all_filtered_elements = set()

from GetPlotStyle import get_plot_style
from GetExpectedLabelsForLegend import get_expected_labels

for (key, df) in all_results_sliced.items():
    key = key.replace('SOC_paramMC_summary_', '')
    
    # Find matching color
    scenario = key.split('_')[0]
    color = colors.get(scenario, '#000000')
    
    # Find matching legend label
    expected_labels = get_expected_labels(key)
    
    # Filter elements using exact matches
    for element in legend_elements:
        if element.get_label() in expected_labels:
            all_filtered_elements.add(element)
    
    # Find matching line style
    style_dict = '-'
    for ttype, style in plot_styles.items():
        if ttype in key:
            style_dict = style
            break
    
    # Find matching hatch style
    hatch = hatch_styles.get(key.split('_')[-1], '')
    
    # Plot mean SOC trajectory
    ax.plot(df['SOC_mean'],
            label=f'SOC - {key}',
            color=color,
            linewidth=2,
            linestyle=style_dict)
    
    # Shaded uncertainty band (±1 SD) with matching color and hatch
    if ShowUncertainty:
        ax.fill_between(
            df.index,  # assumes df is indexed by month; if not, replace with range(len(df))
            df['SOC_mean'] - df['SOC_sd'],
            df['SOC_mean'] + df['SOC_sd'],
            alpha=0.5,
            facecolor='none',  # Makes background transparent
            edgecolor=color,
            hatch=hatch,
            linewidth=1.5
        )

# Set labels and formatting
ax.set_ylabel('SOC (t/ha)')
ax.set_xlabel('Month since initial date')
ax.grid(True)

# Set the legend with filtered elements
final_legend_elements = sorted(list(all_filtered_elements), key=lambda x: x.get_label())
ax.legend(handles=final_legend_elements, loc='best')

plt.tight_layout()
plt.show()

# Save figure
combined_string = ', '.join([element.get_label() for element in final_legend_elements])
plt.savefig(os.path.join(results_dir, f'{combined_string}.png'), dpi=1200)

print("\n" + "=" * 50)
print("🎉 VISUALIZATION COMPLETE!")
print(f"📊 Figure saved to: {results_dir}")
print("=" * 50)


# -----------------------------
# Plot 2: Matrix of final SOC
# -----------------------------
import seaborn as sns
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "browser"  # Use browser to display the figure

# Extract the final delta SOC mean and SD from each scenario dataframe
final_soc = {}
final_soc_sd = {}

for key, df in all_results_sliced.items():
    clean_key = key.replace("SOC_paramMC_summary_", "")
    if 'deltaSOC_mean' in df.columns and 'deltaSOC_sd' in df.columns:
        final_soc[clean_key] = df['deltaSOC_mean'].iloc[-1]
        final_soc_sd[clean_key] = df['deltaSOC_sd'].iloc[-1]

# Convert results to a DataFrame
final_df = pd.DataFrame.from_dict(final_soc, orient='index', columns=['final_SOC'])
final_df['final_SOC_sd'] = pd.Series(final_soc_sd)
final_df.reset_index(inplace=True)
final_df.rename(columns={'index': 'scenario'}, inplace=True)

# Parse scenario parts
final_df[['WS', 'ROT', 'SR']] = final_df['scenario'].str.extract(r'(?P<WS>[^_]+)_(?P<ROT>[^_]+)_(?P<SR>[^_]+)')

final_df['ROT'] = final_df['ROT'].astype(str)
final_df['WS'] = final_df['WS'].astype(float)
final_df['SR'] = final_df['SR'].astype(float)

# Ensure the unique values are sorted for axes
unique_WS = sorted(final_df['WS'].unique())
unique_SR = sorted(final_df['SR'].unique())
unique_ROT = final_df['ROT'].unique()  # categorical, order preserved

fig = px.scatter_3d(
    final_df,
    x='WS',
    y='SR',
    z='final_SOC',
    color='ROT',
    error_z='final_SOC_sd',
    labels={'WS': 'Warming scenario', 'SR': 'Straw return percentage', 'final_SOC': 'Final delta SOC (t/ha)', 'ROT': 'Rotation'},
    title='Interactive 3D Scatter of Final delta SOC by Scenario',
    category_orders={'ROT': unique_ROT}  # ensures only the unique rotations appear
)

# Set axis ticks to only the unique values
fig.update_layout(
    scene=dict(
        xaxis=dict(tickvals=unique_WS),
        yaxis=dict(tickvals=unique_SR)
    )
)

fig.show()

#Find the scenario with minimum/maximum deltaSOC

min_idx = final_df['final_SOC'].idxmin()
min_scenario = final_df.loc[min_idx]

# Calculate confidence interval of the minimum scenario
min_lower = min_scenario['final_SOC'] - min_scenario['final_SOC_sd']
min_upper = min_scenario['final_SOC'] + min_scenario['final_SOC_sd']

print(f"Most favorable scenario for SOC storage:\n{min_scenario}\n")

# Find scenario with maximum final_SOC
max_idx = final_df['final_SOC'].idxmax()
max_scenario = final_df.loc[max_idx]

max_lower = max_scenario['final_SOC'] - max_scenario['final_SOC_sd']
max_upper = max_scenario['final_SOC'] + max_scenario['final_SOC_sd']

print(f"Most negative scenario for SOC storage:\n{max_scenario}\n")



