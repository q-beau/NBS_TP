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

#%% Cell 1: Initialization
import sys, os, numpy as np, subprocess

#Setup working directory
directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(directory)
os.getcwd()

#get the folders to path
function_dir = os.path.join(directory, 'functions')
sys.path.append(function_dir)

# %% Cell 2: Environment Setup and Verification
from setup_environment import setup_environment

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path, results_path, functions_dir, Rscript_exe = setup_environment(script_dir)

# %% Cell 3: Build scenarios and Run RothC
from run_rothc_scenarios import run_rothc_scenarios
succeeded, failed = run_rothc_scenarios(script_dir, data_path, Rscript_exe)

# %% Cell 4: Plot results
import matplotlib.pyplot as plt
%matplotlib qt
from plot_results import plot_results, load_scenarios, plot_best_vs_baseline

final_df, best, worst = plot_results(
    results_dir=os.path.join(script_dir, "results"),
    reporting_years=16,
    show_uncertainty=True,
)
#Extra plot to show SSM vs Basline under similar warming scenario
scen = load_scenarios(results_dir = os.path.join(script_dir, "results"), reporting_years=16)
fig = plot_best_vs_baseline(scen, best, results_dir=os.path.join(script_dir, "results"))
