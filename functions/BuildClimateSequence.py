# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 15:08:10 2025

@author: u230231
"""

import pandas as pd
import numpy as np

def build_climate_sequence_from_calendar(crop_calendar, climate_df, variable_name='Temperature_C'):
    """
    Build a climate sequence (temperature or precipitation) from crop calendar dates
    
    Parameters:
    crop_calendar: DataFrame with crop periods (Start_Date, End_Date)
    climate_df: DataFrame with Year, Month, and climate variable
    variable_name: str, name of the climate variable column
    
    Returns:
    pandas Series of climate values in monthly resolution
    """
    
    # Find the overall date range from crop calendar
    start_date = crop_calendar.iloc[0]['Start_Date']
    end_date = crop_calendar.iloc[-1]['End_Date']
    
    start_year, start_month = map(int, start_date.split('-'))
    end_year, end_month = map(int, end_date.split('-'))
    
    # Calculate total months
    total_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
    
    # Initialize sequence
    climate_sequence = []
    
    # Generate all months from start to end
    current_year, current_month = start_year, start_month
    
    for month_idx in range(total_months):
        current_date_str = f"{current_year}-{current_month:02d}"
        
        # Find climate data for this year/month
        climate_value = climate_df[
            (climate_df['Year'] == current_year) & 
            (climate_df['Month'] == current_month)
        ][variable_name]
        
        if not climate_value.empty:
            climate_sequence.append(climate_value.iloc[0])
        else:
            print(f"Warning: No climate data found for {current_date_str}")
            climate_sequence.append(np.nan)  # or use interpolation/default value
        
        # Move to next month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    
    # Convert to pandas Series
    return pd.Series(climate_sequence, dtype=float)


