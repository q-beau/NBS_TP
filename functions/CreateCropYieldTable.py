# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 13:24:42 2025

@author: u230231
"""

import pandas as pd
import os

def create_yield_table(vegetation_data_path, crop_names_dict, bolinder_coeff_table):
    """
    Create yield table with biomass data and carbon input calculations
    
    Parameters:
    vegetation_data_path: str, path to the vegetation Excel file
    crop_names_dict: dict, mapping of crop names to numeric codes
    bolinder_coeff_path: str, path to Bolinder coefficients CSV file
    
    Returns:
    DataFrame with yield data and carbon inputs
    """
    
    # Load vegetation dataset
    vegetation_dataset = pd.read_excel(vegetation_data_path)
    
    # Build table: average and std harvested biomass per crop species
    yield_table = (
        vegetation_dataset.groupby("Crop species", as_index=False)["Harvested biomass_total_avg (t/ha)"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={
            "mean": "Avg harvested biomass (t/ha)",
            "std": "Std harvested biomass (t/ha)"
        })
    )
    
    # Extract last value of each Mustard sequence for Total_dry_biomass_avg
    mustard_seq = vegetation_dataset['Crop species'] == "Mustard"
    total_dry = vegetation_dataset['Total_dry_biomass_avg (t/ha)']
    
    # Identify last index of each consecutive Mustard sequence
    last_indices = []
    for i in range(len(mustard_seq)):
        if mustard_seq[i]:
            # if next row is different or end of dataset, mark as last
            if i == len(mustard_seq)-1 or not mustard_seq[i+1]:
                last_indices.append(i)
    
    # Select only these last values and compute mean and std
    if last_indices:
        mustard_last_values = total_dry.iloc[last_indices]
        mustard_mean = mustard_last_values.mean()
        mustard_std = mustard_last_values.std()
        
        # Add to yield_table as new row
        yield_table = pd.concat([
            yield_table,
            pd.DataFrame({
                "Crop species": ["Cover crop"],
                "Avg harvested biomass (t/ha)": [mustard_mean],
                "Std harvested biomass (t/ha)": [mustard_std]
            })
        ], axis=0, ignore_index=True)
    
    # Convert into amount of C (remove zero values first)
    yield_table = yield_table[yield_table["Avg harvested biomass (t/ha)"] != 0]
    yield_table["Avg yield (t/ha)"] = yield_table["Avg harvested biomass (t/ha)"] * 0.44  # C content
    yield_table["Std yield (t/ha)"] = yield_table["Std harvested biomass (t/ha)"] * 0.44  # C content
    
    # Add additional crop entries
    additional_crops = [
        {"Crop species": "Rapeseed", "Avg yield (t/ha)": 3, "Std yield (t/ha)": 0.3},
        {"Crop species": "Cameline", "Avg yield (t/ha)": 1.5, "Std yield (t/ha)": 0.15},
        {"Crop species": "Faba", "Avg yield (t/ha)": 3.0, "Std yield (t/ha)": 0.3},
        {"Crop species": "Oat", "Avg yield (t/ha)": 6.8, "Std yield (t/ha)": 0.7},
        {"Crop species": "Pea", "Avg yield (t/ha)": 3.0, "Std yield (t/ha)": 0.3}
    ]
    
    for crop_data in additional_crops:
        crop_row = pd.DataFrame([crop_data])
        yield_table = pd.concat([yield_table, crop_row], ignore_index=True)
    
    # Add numeric code column
    yield_table["Crop code"] = yield_table["Crop species"].map(crop_names_dict)
    
    # Replace missing std by 10% of yield
    yield_table['Std yield (t/ha)'] = yield_table['Std yield (t/ha)'].fillna(yield_table['Avg yield (t/ha)'] * 0.1)

    
    # Merge tables
    merged = yield_table.merge(
        bolinder_coeff_table,
        left_on="Crop species",
        right_on="Crop",
        how="inner"
    )
    
    # Calculate Cin_Bol
    Cp = merged["Avg yield (t/ha)"]
    Cr = (merged["RR"] / merged["RP"]) * Cp
    Cs = (merged["RS"] / merged["RP"]) * Cp
    Ce = (merged["RE"] / merged["RP"]) * Cp
    merged["Cin_Bol"] = Cp * merged["SP"] + Cr * merged["SR"] + Cs * merged["SS"] + Ce * merged["SE"]
    
    # Keep only relevant columns in final yield_table
    final_yield_table = merged[
        ["Crop species", "Avg yield (t/ha)", "Std yield (t/ha)", "Crop code", "Cin_Bol"]
    ]
    
    return final_yield_table

