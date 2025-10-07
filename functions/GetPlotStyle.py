# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 11:35:56 2025

@author: u230231
"""

def get_plot_style(key):
    """
    Extract color and linestyle based on key components
    key format: '8.5_ecofood_ref_50'
    """
    # Color mapping based on first number (scenario)
    color_map = {
        '8.5': '#d62728',  # Red
        '4.5': '#ff7f0e',  # Orange  
        '2.6': '#2ca02c'   # Green
    }
    
    # Linestyle mapping based on diet scenario
    linestyle_map = {
        'ecofood_ref': ':',     # dotted
        'ecofood_vegan': '--',  # dashed
        'baselinesubset': '-'   # full line
    }
    
    # Extract scenario number (first part before underscore)
    scenario = key.split('_')[0]
    
    # Extract diet type (find which diet scenario is in the key)
    linestyle = '-'  # default
    for diet, style in linestyle_map.items():
        if diet in key:
            linestyle = style
            break
    
    # Get color (default to black if not found)
    color = color_map.get(scenario, '#000000')
    
    return color, linestyle