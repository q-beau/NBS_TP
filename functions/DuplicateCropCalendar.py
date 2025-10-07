# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 10:51:25 2025
@author: u230231
"""
import pandas as pd

def duplicate_crop_calendar(crop_calendar, n_duplications):
    """
    Duplicate the crop calendar n times with updated dates and rotations
    Fill gaps between rotations by extending cover crop duration
    
    Parameters:
    crop_calendar: DataFrame with the base crop calendar
    n_duplications: number of times to duplicate (e.g., 2 means original + 2 copies = 3 total)
    
    Returns:
    DataFrame with duplicated crop calendar without gaps
    """
    
    duplicated_calendars = []
    
    for i in range(n_duplications + 1):  # +1 to include original
        calendar_copy = crop_calendar.copy()
        
        # Update rotation number
        calendar_copy['Rotation'] = f'Rotation {i + 1}'
        
        # Add years to dates (each cycle is ~8 years)
        years_to_add = i * 8
        calendar_copy['Start_Date'] = calendar_copy['Start_Date'].apply(
            lambda x: f"{int(x.split('-')[0]) + years_to_add}-{x.split('-')[1]}"
        )
        calendar_copy['End_Date'] = calendar_copy['End_Date'].apply(
            lambda x: f"{int(x.split('-')[0]) + years_to_add}-{x.split('-')[1]}"
        )
        
        duplicated_calendars.append(calendar_copy)
    
    # Combine all calendars
    final_calendar = pd.concat(duplicated_calendars, ignore_index=True)
    
    # Fill gaps by extending cover crop at end of each rotation to connect with next
    for i in range(len(final_calendar) - 1):
        current_end = final_calendar.iloc[i]['End_Date']
        next_start = final_calendar.iloc[i + 1]['Start_Date']
        
        # Check if there's a gap
        current_year, current_month = map(int, current_end.split('-'))
        next_year, next_month = map(int, next_start.split('-'))
        
        # Calculate if there's a gap (more than 1 month difference)
        current_total_months = current_year * 12 + current_month
        next_total_months = next_year * 12 + next_month
        
        if next_total_months > current_total_months + 1:
            # There's a gap - extend current period to fill it
            gap_end_year = next_year
            gap_end_month = next_month - 1
            
            # Handle year boundary
            if gap_end_month == 0:
                gap_end_month = 12
                gap_end_year -= 1
            
            final_calendar.iloc[i, final_calendar.columns.get_loc('End_Date')] = f"{gap_end_year}-{gap_end_month:02d}"
    
    return final_calendar
