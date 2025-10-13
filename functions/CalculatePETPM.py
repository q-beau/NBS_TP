# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 15:34:22 2025

@author: u230231
"""

import numpy as np
import pandas as pd

def calculate_pet_penman_monteith(temp_c, rh_percent, shortwave_rad, month_series=None, latitude=50.56):
    """
    Calculate potential evapotranspiration using Penman-Monteith equation with shortwave radiation
    
    Parameters:
    temp_c: Series/array, monthly temperature in °C
    rh_percent: Series/array, monthly relative humidity in %
    shortwave_rad: Series/array, shortwave radiation in W/m² (or MJ/m²/day if specified)
    month_series: Series/array, month numbers (1-12) for each observation
    latitude: float, latitude in degrees (default: Gembloux ~50.56°N)
    
    Returns:
    Series of PET in mm/month ==> simplified by *30, but ideally should provide the numb of days per months
    """
    
    # Constants
    gamma = 0.665  # psychrometric constant (kPa/°C)
    albedo = 0.23  # grass reference albedo
    sigma = 4.903e-9  # Stefan-Boltzmann constant (MJ K⁻⁴ m⁻² day⁻¹)
    
    # Convert temperature to Kelvin for some calculations
    temp_k = temp_c + 273.15
    
    # Saturation vapor pressure (kPa) - Tetens formula
    e_sat = 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))
    
    # Actual vapor pressure (kPa)
    e_actual = e_sat * (rh_percent / 100)
    
    # Vapor pressure deficit (kPa)
    vpd = e_sat - e_actual
    
    # Slope of saturation vapor pressure curve (kPa/°C)
    delta = (4098 * e_sat) / ((temp_c + 237.3) ** 2)
    
    # Convert shortwave radiation
    # If in W/m², convert to MJ/m²/day
    if shortwave_rad.max() > 50:  # Likely in W/m²
        rs = shortwave_rad * 0.0864  # W/m² to MJ/m²/day
    else:  # Already in MJ/m²/day
        rs = shortwave_rad
    
    # Net shortwave radiation (MJ/m²/day)
    rns = (1 - albedo) * rs
    
    # Clear sky radiation (approximation for net longwave calculation)
    # Extraterrestrial radiation calculation
    if month_series is not None:
        lat_rad = latitude * np.pi / 180  # latitude in radians
        
        # Julian day approximation from month
        julian_day = pd.Series([15 + 30 * (m - 1) for m in month_series])  # mid-month approximation
        
        # Solar declination
        declination = 0.409 * np.sin(2 * np.pi * julian_day / 365 - 1.39)
        
        # Sunset hour angle
        ws = np.arccos(-np.tan(lat_rad) * np.tan(declination))
        
        # Extraterrestrial radiation
        dr = 1 + 0.033 * np.cos(2 * np.pi * julian_day / 365)
        ra = (24 * 60 / np.pi) * 0.082 * dr * (
            ws * np.sin(lat_rad) * np.sin(declination) + 
            np.cos(lat_rad) * np.cos(declination) * np.sin(ws)
        )
        
        # Clear sky radiation
        rso = (0.75 + 2e-5 * 0) * ra  # assuming elevation = 0 for simplicity
    else:
        rso = rs * 1.35  # simple approximation
    
    # Net longwave radiation (MJ/m²/day)
    rnl = sigma * (temp_k ** 4) * (0.34 - 0.14 * np.sqrt(e_actual)) * (1.35 * rs / rso - 0.35)
    
    # Net radiation (MJ/m²/day)
    rn = rns - rnl
    
    # Soil heat flux (assumed negligible for monthly data)
    g = 0
    
    # Wind speed (assume 2 m/s if not available)
    u2 = 2.0
    
    # Penman-Monteith equation (mm/day)
    numerator = 0.408 * delta * (rn - g) + gamma * 900 / (temp_c + 273) * u2 * vpd
    denominator = delta + gamma * (1 + 0.34 * u2)
    
    pet = numerator / denominator
    
    # Ensure non-negative values
    pet = np.maximum(pet, 0) * 30
    
    return pet




