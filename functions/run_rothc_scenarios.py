# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 15:06:41 2026

@author: qbeau
"""

import os
import subprocess
import configparser
from itertools import product

import pandas as pd

from CreateRothCDataIn import CreateRothCDataIn


def run_rothc_scenarios(script_dir, data_path, Rscript_exe,
                        config_file="param.ini", r_script=("rothc", "rothc_MC.R"),
                        verbose=False):
    """Run RothC for every combination of warming, straw-return and rotation scenarios.

    For each combination, the RothC input table is built, saved as
    data/DataRothCRun.csv and the R Monte Carlo script is executed.

    Parameters
    ----------
    script_dir : str
        Project root (contains param.ini, data/ and rothc/).
    data_path : str
        Folder with the input data passed to CreateRothCDataIn.
    Rscript_exe : str
        Path to Rscript.exe.
    config_file : str
        Name of the configuration file located in script_dir.
    r_script : tuple of str
        Path components of the R script, relative to script_dir.
    verbose : bool
        Print the R standard output after each successful run.

    Returns
    -------
    succeeded, failed : lists of scenario identifiers (WS_ROT_SR)
    """
    print("CELL 2: LAUNCH ROTHC")
    print("=" * 50)

    # ---- Read scenarios from param.ini -----------------------------------
    config_path = os.path.join(script_dir, config_file)
    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Available: warming 8.5, 4.5, 2.6; rotation ecofoodref, ecofoodvegan,
    # baselinesubset; straw return between 0 and 100 (%)
    warming_scenarios = [s.strip() for s in config["Scenarios"]["warming_scenarios"].split(",")]
    straw_scenarios = [int(s) for s in config["Scenarios"]["straw_scenarios"].split(",")]
    rotation_scenarios = [s.strip() for s in config["Scenarios"]["rotation_scenarios"].split(",")]

    combinations_ = list(product(warming_scenarios, straw_scenarios, rotation_scenarios))
    print(f"{len(combinations_)} scenario(s) to run "
          f"({len(warming_scenarios)} WS x {len(straw_scenarios)} SR x "
          f"{len(rotation_scenarios)} ROT)")

    # ---- Paths -----------------------------------------------------------
    r_script_path = os.path.join(script_dir, *r_script)
    run_csv = os.path.join(script_dir, "data", "DataRothCRun.csv")
    if not os.path.exists(Rscript_exe):
        raise FileNotFoundError(f"Rscript not found: {Rscript_exe}")
    if not os.path.exists(r_script_path):
        raise FileNotFoundError(f"R script not found: {r_script_path}")

    succeeded, failed = [], []

    # ---- Loop over all combinations --------------------------------------
    for n, (warming, straw, rotation) in enumerate(combinations_, start=1):
        scenario_id = f"{warming}_{rotation}_{straw}"
        print(f"\n[{n}/{len(combinations_)}] Scenario {scenario_id}")

        # Build the RothC input table and save it for the R script
        data_in, _ = CreateRothCDataIn(data_path, warming, straw, rotation)
        data_in["Scenario"] = scenario_id
        data_in.to_csv(run_csv, index=False)

        # Run RothC in R
        try:
            result = subprocess.run([Rscript_exe, r_script_path], check=True,
                                    capture_output=True, text=True)
            print("  RothC executed successfully")
            if verbose and result.stdout:
                print("  R output:\n", result.stdout)
            succeeded.append(scenario_id)
        except subprocess.CalledProcessError as e:
            print("  RothC FAILED")
            print("  STDOUT:\n", e.stdout)
            print("  STDERR:\n", e.stderr)
            failed.append(scenario_id)

    # ---- Summary ---------------------------------------------------------
    print("\n" + "=" * 50)
    print(f"Completed: {len(succeeded)} succeeded, {len(failed)} failed")
    if failed:
        print("Failed scenarios: " + ", ".join(failed))
    print("=" * 50)

    return succeeded, failed