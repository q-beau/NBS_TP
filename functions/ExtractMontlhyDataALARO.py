# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 14:09:56 2025

@author: u230231
"""

import xarray as xr
import pandas as pd
import os
import glob
from pathlib import Path
import numpy as np

def extract_monthly_data_ALARO(folder_path, lat_target, lon_target, var_target, buffer=0.1):
    """
    Extract monthly temperature data from NetCDF files for a specific location
    
    Parameters:
    folder_path: str, path to folder containing NetCDF files
    lat_target: float, target latitude (e.g., 50.5639 for Gembloux)
    lon_target: float, target longitude (e.g., 4.9994 for Gembloux)
    buffer: float, buffer around target coordinates for selection
    
    Returns:
    DataFrame with year, month, and mean temperature
    """
    
    # Get all NetCDF files in the folder
    nc_files = glob.glob(os.path.join(folder_path, "*.nc"))
    
    if not nc_files:
        print(f"No NetCDF files found in {folder_path}")
        return pd.DataFrame()
    
    all_monthly_data = []
    
    for file_path in sorted(nc_files):
        try:
            # Load the NetCDF file
            ds = xr.open_dataset(file_path)
            print(f"Processing {os.path.basename(file_path)}")
            
            # Extract year from filename
            filename = os.path.basename(file_path)
            import re
            year_match = re.search(r'(\d{4})', filename)
            year = int(year_match.group(1)) if year_match else None
            
            # Select data for the target location (with buffer)
            ds_location = ds.sel(
                lat=slice(lat_target - buffer, lat_target + buffer),
                lon=slice(lon_target - buffer, lon_target + buffer)
            )
     
            
            # Get temperature data
            if var_target == 'Temperature':
                temp_var = 'tas'
                temp_label = 'Temperature_C'
            elif var_target == 'Precipitation': 
                temp_var = 'pr'
                temp_label = 'Precipitation_mm'
            elif var_target == 'Humidity':
                temp_var = 'hurs'
                temp_label = 'RelHumidity_%'     
            elif var_target == 'Radiation':
                temp_var = 'rsds'
                temp_label = 'NetRad_Wm-2'  
                
            temp_data = ds_location[temp_var]
            
            # Group by month and calculate monthly means
            monthly_temps = temp_data.groupby('time.month').mean()
            
            # Convert from Kelvin to Celsius if needed
            if temp_var == 'tas':  # Likely in Kelvin
                monthly_temps = monthly_temps - 273.15
            
            # Create monthly records
            for month in range(1, 13):
                if month in monthly_temps.month:
                    if var_target == ('Temperature') or var_target == ('Humidity') or var_target == ('Radiation'):
                        month_temp = np.mean((monthly_temps.sel(month=month).values))                      
                    elif var_target == 'Precipitation':
                        month_temp = np.sum((monthly_temps.sel(month=month).values)*86400)
                        
                    all_monthly_data.append({
                        'Year': year,
                        'Month': month,
                        temp_label : month_temp,
                        'Date': f"{year}-{month:02d}",
                        'Filename': filename
                    })
            
            ds.close()
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    # Create DataFrame
    df_monthly = pd.DataFrame(all_monthly_data)
    df_monthly = df_monthly.sort_values(['Year', 'Month']).reset_index(drop=True)
    
    return df_monthly





