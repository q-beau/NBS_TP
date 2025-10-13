# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 09:53:46 2025

@author: u230231
"""
import pandas as pd
import numpy as np
def transform_agb_rothc(series):
    series = series.copy()
    values = series.values
    
    i = 0
    while i < len(values):
        if pd.isna(values[i]) or values[i] == 0:
            i += 1
            continue
        
        # find end of block of identical values
        j = i
        while j + 1 < len(values) and values[j+1] == values[i]:
            j += 1
        
        block_value = values[i]
        
        # set all to 0
        values[i:j+1] = 0.0
        
        # last index gets half
        values[j] = block_value / 2.0
        
        # three previous indices (if available) get 1/6
        for k in range(max(i, j-3), j):
            values[k] = block_value / 6.0
        
        i = j + 1
        
        # Convert back to pandas Series and then fill NaN values
        result_series = pd.Series(values, index=series.index, name=series.name)
        result_series = result_series.fillna(0)  # Apply fillna to the Series, not numpy array
   
    return result_series
