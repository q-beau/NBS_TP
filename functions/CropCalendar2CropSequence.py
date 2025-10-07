# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 13:08:30 2025

@author: u230231
"""

import pandas as pd
from datetime import datetime

def crop_calendar_to_sequence(crop_calendar):
    """
    Convert crop calendar back to monthly crop sequence
    
    Parameters:
    crop_calendar: DataFrame with crop periods
    
    Returns:
    pandas Series of crop codes in monthly resolution
    """
    
    # Find the overall date range
    start_date = crop_calendar.iloc[0]['Start_Date']
    end_date = crop_calendar.iloc[-1]['End_Date']
    
    start_year, start_month = map(int, start_date.split('-'))
    end_year, end_month = map(int, end_date.split('-'))
    
    # Calculate total months
    total_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
    
    # Initialize sequence
    crop_sequence = []
    
    # Generate all months from start to end
    current_year, current_month = start_year, start_month
    
    for month_idx in range(total_months):
        current_date_str = f"{current_year}-{current_month:02d}"
        
        # Find which crop period this month belongs to
        crop_found = False
        for _, row in crop_calendar.iterrows():
            period_start = row['Start_Date']
            period_end = row['End_Date']
            
            # Check if current month is within this period
            if period_start <= current_date_str <= period_end:
                crop_sequence.append(row['Crop'])
                crop_found = True
                break
        
        if not crop_found:
            print(f"Warning: No crop found for {current_date_str}")
            crop_sequence.append(1)  # Default to bare soil
        
        # Move to next month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    
    # Convert to pandas Series
    return pd.Series(crop_sequence, dtype=float)




