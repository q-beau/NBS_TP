# -*- coding: utf-8 -*-
"""
Nature-Based Solutions for Climate Change Mitigation
=====================================================

Practical Session: Soil Organic Carbon Modeling with RothC
-----------------------------------------------------------

This exercise simulates soil organic carbon (SOC) stock changes in the future using
the RothC model (Jenkison et al., 2014). The model requires climate data (precipitation,
temperature, evapotranspiration), carbon (C) inputs from biomass, farmyard manure, and
soil cover information.

Overview
--------
C inputs from biomass are derived from crop yield and allocation coefficients provided
by Bolinder et al. (2007). Model simulations are impacted by:

- **Global warming scenarios**: RCP 2.6, 4.5, and 8.5
- **Crop rotations**: baselinesubset, ecofood_ref, ecofood_vegan
- **Straw return percentages**: 0%, 50%, 100%

These three levels of scenario modalities create 27 possible climate-rotation-straw
combinations when three straw return scenarios are selected.

References
----------
- Jenkison et al. (2014) - RothC model documentation
- Bolinder et al. (2007) - Crop allocation coefficients
- Penman (1948) - Penman-Monteith equation for evapotranspiration

ALARO Climate Data
------------------
ALARO data are available as NetCDF files at:
https://ac.ngi.be/catalogue?language=en&openpath=GeoBePartners-open%2FBelgianClimateCentre

Created on Thu Sep 18 10:15:38 2025

@author: qbeau
"""

#!/usr/bin/env python3

#%% Cell 1: Environment Setup and Verification

"""
CELL 1: Environment Setup and Package Verification
===================================================

Purpose
-------
This cell verifies that the correct conda environment (NBS_TP) is active and prepares
the workspace by:

1. Checking Python environment and version
2. Setting up directory paths (data, results, functions)
3. Verifying required packages are installed
4. Cleaning previous results from earlier runs

Expected Behavior
-----------------
The script will display:

- ✅ Success messages if everything is configured correctly
- ⚠️ Warnings if packages are missing or directories don't exist
- ❌ Errors that stop execution if the wrong environment is active

Troubleshooting
---------------
If you see a warning about the wrong conda environment:

1. Close Spyder completely
2. Open Anaconda Prompt
3. Run: ``conda activate NBS_TP``
4. Run: ``spyder``
5. Reopen this script

Required Packages
-----------------
- numpy
- pandas
- matplotlib

These should be installed in the NBS_TP environment. If missing, run in Anaconda Prompt::

    conda activate NBS_TP
    conda install numpy pandas matplotlib

Directory Verification
----------------------
The script checks for the existence of:

- ``data/`` folder: Contains input files and climate data
- ``results/`` folder: Stores RothC model outputs
- ``functions/`` folder: Contains CreateRothCDataIn function

If any folders are missing, the script will raise a FileNotFoundError.

Cleaning Previous Results
--------------------------
Old result files matching these patterns are removed:

- ``data/DataRothCRun_*.csv``
- ``results/*.csv``

This ensures each run starts with a clean slate.
"""

print("🔧 CELL 1: ENVIRONMENT SETUP")
print("=" * 50)

import sys, os, glob

# Check if in correct environment
print(f"🐍 Using Python: {sys.executable}")
print(f"🐍 Python version: {sys.version.split()[0]}")

if 'NBS_TP' not in sys.executable:
    print("\n⚠️ WARNING: You may not be in the correct conda environment!")
    print("💡 Please close Spyder and follow these steps:")
    print("   1. Open Anaconda Prompt")
    print("   2. Run: conda activate NBS_TP")
    print("   3. Run: spyder")
    print("   4. Reopen this script")
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


# %% Cell 2: Build RothC scenarios from the baseline

"""
CELL 2: Launch RothC Simulations
=================================

Purpose
-------
This cell generates input files for the RothC model and executes simulations for all
combinations of warming scenarios, straw return percentages, and crop rotations.

Main Actions
------------
1. Configure scenario variables (warming, straw return, rotations)
2. Generate input data files using CreateRothCDataIn function
3. Execute RothC model in R for each scenario combination
4. Save results to the results folder

Scenario Configuration
----------------------

Climate Scenarios (Warming Scenarios)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Weather forecasts over the 2025-2100 period are needed for future simulations. The
ALARO climate model generated data over Gembloux for three IPCC representative
concentration pathways (RCP):

- **RCP 2.6**: Low emission scenario (radiative forcing +2.6 W/m² by 2100)
- **RCP 4.5**: Intermediate stabilization scenario (+4.5 W/m² by 2100)
- **RCP 8.5**: High emission scenario (+8.5 W/m² by 2100)

These values represent expected changes in radiative forcing from 1750 to 2100.

ALARO datasets include:

- Precipitation
- Temperature
- Relative humidity (for Penman-Monteith evapotranspiration calculation)
- Net radiation (for Penman-Monteith evapotranspiration calculation)

Monthly climate data are available in the data folder as ``ALARO_P_RCP-2.6.csv``,
``ALARO_P_RCP-4.5.csv``, and ``ALARO_P_RCP-8.5.csv``.

Straw Return Scenarios
^^^^^^^^^^^^^^^^^^^^^^
The amount of straw returned to soil after harvest can be adjusted by modifying
Bolinder coefficients in ``data/CoeffBolinder.csv``. In the original coefficients,
15% of straw is returned (85% exported).

The straw return percentage directly impacts the 'SS' coefficient for winter wheat:

.. math::
    SS = 1 - \\text{straw_scenario}

Where straw_scenario is expressed as a fraction (e.g., 0.5 for 50%).

In this exercise, three straw scenarios are defined:

- **0%**: All straw exported (SS = 1.0)
- **50%**: Half straw returned (SS = 0.5)
- **100%**: All straw returned (SS = 0.0)

Crop Rotation Scenarios
^^^^^^^^^^^^^^^^^^^^^^^^
Three crop rotation systems are compared:

1. **baselinesubset**: Typical 4-year rotation (16-year subset from Lonzée site)
2. **ecofood_ref**: Modified baseline with root crops replaced by cereals (8-year, duplicated)
3. **ecofood_vegan**: Vegan rotation without root crops (8-year, duplicated)

Crop calendars for each rotation are provided as:

- ``crop_calendar_baselinesubset.csv``
- ``crop_calendar_ecofood_ref.csv``
- ``crop_calendar_ecofood_vegan.csv``

These CSV files contain start and end dates for each crop, which are used by
CreateRothCDataIn to calculate:

1. **Soil cover factor**: Duration of vegetation cover
2. **Carbon inputs**: Amount of C returned to soil at harvest

CreateRothCDataIn Function
--------------------------
This function generates the RothC input file by:

1. Loading climate data for the specified warming scenario
2. Loading crop calendar for the specified rotation
3. Adjusting Bolinder coefficients based on straw return percentage
4. Calculating C inputs from biomass measurements (``BE-Lon_vegetation data.xlsx``)
5. Combining all inputs into a RothC-compatible CSV file

Parameters
^^^^^^^^^^
- ``data_path`` (str): Path to data folder (automatically detected)
- ``warming_scenario`` (str): '2.6', '4.5', or '8.5'
- ``straw_scenario`` (int): Percentage of straw returned (0, 50, or 100)
- ``rotation_scenario`` (str): 'baselinesubset', 'ecofood_ref', or 'ecofood_vegan'

Returns
^^^^^^^
pandas.DataFrame: RothC input data with monthly climate, C inputs, and soil cover

Carbon Input Distribution
--------------------------
In RothC, carbon inputs at harvest are distributed as follows:

- **50%** added to the harvest month
- **50%** equally distributed over the three months before harvest

R Script Execution
------------------
The RothC model is implemented in R (``rothc/rothc_MC.R``). For each scenario
combination, this script:

1. Reads the input CSV file (``data/DataRothCRun.csv``)
2. Runs Monte Carlo simulations with parameter uncertainty
3. Saves results as ``SOC_paramMC_summary_{climate}_{rotation}_{straw}.csv``

Configuration
^^^^^^^^^^^^^
**Important**: Set ``Rpath`` to your R installation directory before running.

Example paths::

    Rpath = fr"C:\\Program Files\\R\\R-4.4.2\\bin\\x64"  # Standard installation
    Rpath = fr'C:\\Users\\username\\AppData\\Local\\Programs\\R\\R-43~1.2\\bin\\x64'  # User installation

Expected Output
---------------
After execution, the results folder will contain 27 CSV files (3 warming × 3 rotation
× 3 straw scenarios), each named::

    SOC_paramMC_summary_{warming}_{rotation}_{straw}.csv

Each file contains monthly SOC predictions with uncertainty estimates.

Troubleshooting
---------------
If the R script fails to execute:

1. Verify R is installed and Rpath is correct
2. Check that ``rothc/rothc_MC.R`` exists
3. Ensure R packages are installed (check rothc_MC.R for dependencies)
4. Review error messages in STDERR output
"""

print("🔧 CELL 2: LAUNCH ROTHC")
print("=" * 50)

import numpy as np
import pandas as pd
import os
import glob
import subprocess
import matplotlib.pyplot as plt
from itertools import combinations

#------------------ Script variables ---------------------------------------#

# Set Rpath here (where R.exe is located)
# IMPORTANT: Modify this path to match your R installation directory
# Rpath = fr"C:\Program Files\R\R-4.4.2\bin\x64"  # Example for standard installation
Rpath = fr'C:\Users\u230231\AppData\Local\Programs\R\R-43~1.2\bin\x64'
# Rpath = r'C:\Users\u230231\AppData\Local\anaconda3\envs\rstudio\Scripts\Rterm.exe' #via anaconda

# Define scenario combinations
warming_scenarios = ['8.5','4.5','2.6']  # RCP scenarios: 8.5, 4.5, or 2.6
step_straw_return = 50
straw_scenarios = list(range(0, 101, step_straw_return))  # 0%, 50%, 100% straw return
rotation_scenarios = ['baselinesubset','ecofood_ref','ecofoodvegan']  # Three rotation types

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
            DataRothCIn = CreateRothCDataIn(data_path, warming_scenario, 
                                           straw_scenario, rotation_scenario)
            
            # Add scenario identifier to the dataframe
            DataRothCIn['Scenario'] = warming_scenario + '_' + rotation_scenario + '_' + str(straw_scenario)
            
            # Save as CSV for RothC to read
            DataRothCIn.to_csv(os.path.join(script_dir, 'data','DataRothCRun.csv'), index=False)
            
            # Setup R environment
            RscriptFileName = os.path.join(script_dir, 'rothc', 'rothc_MC.R')
            Rscript_exe = os.path.join(Rpath, "Rscript.exe")
            
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

"""
CELL 3: Visualize RothC Results
================================

Purpose
-------
This cell loads RothC simulation results and creates publication-quality visualizations
showing SOC stock evolution over time with uncertainty bands.

Visualization Features
----------------------
The plotting system uses a three-dimensional visual encoding:

1. **Color**: Represents warming scenarios (WS)
   
   - RCP 2.6: Blue (#a1afde)
   - RCP 4.5: Orange (#fbc464)
   - RCP 8.5: Red (#954130)

2. **Line style**: Represents crop rotations (ROT)
   
   - ecofood_ref: Dotted line (':')
   - ecofood_vegan: Solid line ('-')
   - baselinesubset: Dash-dot line ('-.')

3. **Hatch pattern**: Represents straw return scenarios (SR)
   
   - 0%: No hatch (light gray fill)
   - 50%: Horizontal lines ('---')
   - 100%: Plus signs ('+++')

Result File Selection
---------------------
The ``SelectCrit`` variable controls which CSV files are loaded and plotted:

Options
^^^^^^^
- ``'All'``: Load all 27 result files
- ``'WS'``: Select specific warming scenario (requires ``SelectWS``)
- ``'ST'``: Select specific straw return (requires ``SelectST``)
- ``'WS+ST'``: Select warming + straw combination
- ``'WS+ROT'``: Select warming + rotation combination

Example
^^^^^^^
To visualize all straw return scenarios for RCP 2.6 with ecofood_ref rotation::

    SelectCrit = 'WS+ROT'
    SelectWS = '2.6'
    SelectROT = 'ecofood_ref'

This will load three files:

- ``SOC_paramMC_summary_2.6_ecofood_ref_0.csv``
- ``SOC_paramMC_summary_2.6_ecofood_ref_50.csv``
- ``SOC_paramMC_summary_2.6_ecofood_ref_100.csv``

Result File Structure
---------------------
Each RothC output CSV contains:

Columns
^^^^^^^
- **Month**: Simulation month (0 to total simulation length)
- **SOC_mean**: Mean SOC stock (t/ha)
- **SOC_sd**: Standard deviation of SOC stock (t/ha)
- **Delta_SOC_mean**: Change in SOC from initial value (t/ha)
- **Delta_SOC_sd**: Standard deviation of SOC change (t/ha)

The uncertainty estimates come from Monte Carlo simulations with RothC parameter
uncertainty propagation.

Plot Components
---------------

Main Plot
^^^^^^^^^
- **X-axis**: Month since initial date
- **Y-axis**: SOC stock (t/ha)
- **Line plots**: Mean SOC evolution (``ax.plot``)
- **Shaded bands**: ±1 standard deviation uncertainty (``ax.fill_between``)

The shaded uncertainty bands are transparent with hatching patterns that indicate
the straw return scenario. The edge color of the hatch matches the line color
(warming scenario).

Legend
^^^^^^
The legend displays all visual encoding elements present in the selected data:

- Color patches for each warming scenario
- Line style examples for each rotation
- Hatch patterns for each straw return level

Only combinations actually present in the data are shown in the legend.

Output
------
The final figure is saved as a PNG file in the results folder with a filename
constructed from all legend elements::

    results/WS 2.6, ecofood_ref, SR 0, SR 50, SR 100.png

The figure resolution is set to 1200 DPI for publication quality.

Interactive Visualization
-------------------------
The magic command ``%matplotlib qt`` enables interactive plotting in a separate
window, allowing zoom, pan, and exploration of the results.

Example Result
--------------
A typical plot shows:

- Multiple SOC trajectories over 75 years (2025-2100)
- Uncertainty bands showing Monte Carlo parameter uncertainty
- Clear visual distinction between scenarios using color/line/hatch encoding
- Grid lines for easier value reading
- Comprehensive legend explaining all visual elements

Troubleshooting
---------------
If no plots appear:

1. Check that result CSV files exist in the results folder
2. Verify SelectCrit matches available files
3. Ensure matplotlib backend is properly configured
4. Check console for error messages during file loading
"""

print("🔧 CELL 3: PLOT RESULTS")
print("=" * 50)

%matplotlib qt

# Load the result files from RothC
results_dir = os.path.join(script_dir, "results")

# Select the csv files: either all, or select a specific scenario
SelectCrit = 'WS+ROT'  # either 'All', 'WS', 'ST', 'WS+ST','WS+ROT'
SelectWS = '2.6'
# SelectST = '100'
SelectROT = 'ecofood_ref'

if SelectCrit == 'All':
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
elif SelectCrit == 'WS+ST':
    csv_files = glob.glob(os.path.join(results_dir, f"*{SelectWS}*{SelectST}*.csv"))
elif SelectCrit == 'WS+ROT':
    csv_files = glob.glob(os.path.join(results_dir, f"*{SelectWS}*{SelectROT}*.csv"))

all_results = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f) for f in csv_files}

# -----------------------------
# Plot 1: SOC time series overlayed
# -----------------------------

# Define colors for different WS
colors = {
    '2.6': '#a1afde',  # Blue
    '4.5': '#fbc464',  # Orange
    '8.5': '#954130',  # Red
}

# Define line styles for different ROT
plot_styles = {
    'ecofood_ref': ':',
    'ecofood_vegan': '-',
    'baselinesubset': '-.'
}

# Define hatch patterns for different SR
hatch_styles = {
    '0': '',
    '50': '-',
    '100': '+'
}

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

for (key, df) in all_results.items():
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
