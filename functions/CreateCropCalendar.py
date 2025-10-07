# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 08:49:00 2025

@author: u230231
"""
import pandas as pd
from datetime import datetime


def create_crop_calendar(crop_sequence, crop_names, start_date):
    """
    Create a crop calendar from a sequence of monthly crop codes
    
    Parameters:
    crop_sequence: list/array of crop codes (monthly data)
    crop_names: dictionary mapping crop codes to crop names
    start_date: datetime object for the start date (default: March 2004)
    
    Returns:
    DataFrame with crop periods showing crop code, name, dates, duration, and rotation
    """
    
    # Generate dates for each month in the sequence
    dates = []
    for i in range(len(crop_sequence)):
        year = start_date.year + (start_date.month + i - 1) // 12
        month = (start_date.month + i - 1) % 12 + 1
        dates.append(datetime(year, month, 1))
    
    # Group consecutive months with same crop
    crop_periods = []
    i = 0
    
    while i < len(crop_sequence):
        current_crop = crop_sequence[i]
        start_idx = i
        
        # Find end of current crop period
        while i < len(crop_sequence) and crop_sequence[i] == current_crop:
            i += 1
        
        end_idx = i - 1
        
        crop_periods.append({
            'Crop': int(current_crop),
            'Start_Date': dates[start_idx].strftime('%Y-%m'),
            'End_Date': dates[end_idx].strftime('%Y-%m')
            # 'Duration_Months': end_idx - start_idx + 1,
            # 'Start_Month_Index': start_idx,
            # 'End_Month_Index': end_idx
        })
    
    # Create DataFrame
    crop_calendar = pd.DataFrame(crop_periods)
    
    # Add Crop_Name column after Crop column
    crop_names_reverse = {v: k for k, v in crop_names.items()}
    crop_calendar.insert(1, 'Crop_Name', crop_calendar['Crop'].map(crop_names_reverse))
    
    # Define rotation periods based on start dates
    def get_rotation(start_date_str):
        year, month = map(int, start_date_str.split('-'))
        
        if (year == start_date.year and month >= 3) or year < start_date.year+4:
            return 'Rotation 1'
        elif year < start_date.year+8:
            return 'Rotation 2'
        elif year < start_date.year+12:
            return 'Rotation 3'
        elif year < start_date.year+16:
            return 'Rotation 4'
        else:  # 2020 onwards until 2024-07
            return 'Rotation 5'
    
    # Add Rotation column
    crop_calendar['Rotation'] = crop_calendar['Start_Date'].apply(get_rotation)
    
    return crop_calendar

