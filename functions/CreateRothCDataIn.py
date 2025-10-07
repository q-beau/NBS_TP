# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 09:52:07 2025

@author: u230231
"""
import pandas as pd
import os 
import numpy as np

def CreateRothCDataIn(data_path,warming_scenario,straw_scenario,management_scenario,setzeroFYM = False):
    #Load climate variables
    monthly_rn_df = pd.read_csv(os.path.join(data_path, f'ALARO_Rn_RCP-{warming_scenario}.csv'))
    monthly_rh_df = pd.read_csv(os.path.join(data_path, f'ALARO_RH_RCP-{warming_scenario}.csv'))
    monthly_pr_df = pd.read_csv(os.path.join(data_path, f'ALARO_P_RCP-{warming_scenario}.csv'))
    monthly_temp_df = pd.read_csv(os.path.join(data_path, f'ALARO_T_RCP-{warming_scenario}.csv'))
    # #Load initial data file input
    # DataRothC = pd.read_csv(os.path.join(data_path, f'DataRothCRun_{management_scenario}.csv'))
    
    crop_names = {
        'Bare soil': 1,
        'Cover crop': 2, 
        'Green dwarf bean': 3,  # Note: your data has "Green dwarf bean" not "Green dwarf beans"
        'Maize': 4,
        'Potato': 5,
        'Sugar beet': 6,
        'Winter Wheat': 7,  # Note: your data has "Winter Wheat" not "Winter wheat"
        'Rapeseed': 8,
        'Cameline': 9,
        'Faba': 10,
        'Pea': 11,
        'Oat': 12
    }
    
    #Create yield table after straw_scenario
    from CreateCropYieldTable import create_yield_table
    CoeffBolinder = pd.read_csv(os.path.join(data_path, 'CoeffBolinder.csv')) #open the CoeffBolinder table
    CoeffBolinder.loc[CoeffBolinder['Crop'] == 'Winter Wheat',['SS']] = straw_scenario/100
    yield_table = create_yield_table(
        vegetation_data_path=os.path.join(data_path, 'BE-Lon_vegetation data.xlsx'),
        crop_names_dict=crop_names,
        bolinder_coeff_table=CoeffBolinder)
    #Create yield table
    cinbol_map = dict(zip(yield_table["Crop code"], yield_table["Cin_Bol"]))
    
    #Create crop sequence after management scenario
    crop_calendar = pd.read_csv(os.path.join(data_path, f'crop_calendar_{management_scenario}.csv'))
    from CropCalendar2CropSequence import crop_calendar_to_sequence
    crop_sequence = crop_calendar_to_sequence(crop_calendar)
    
    #Create SoilCover sequence after management scenario
    soilcover_sequence = crop_sequence.apply(lambda x: 1.0 if x == 1 else 0.6)
    
    #Create AGB sequence after management scenario
    from TransformAGBRothC import transform_agb_rothc
    AGB_sequence = transform_agb_rothc(crop_sequence.map(cinbol_map)) #create modified AGB sequence

    #Create FYM sequence after management scenario
    if setzeroFYM:
        FYM_sequence = pd.Series(np.zeros(len(AGB_sequence)), name='FYM')
    else:
        FYM_mean_per_rot = 2.69 #avg t/ha per rotation from baseline scenario
        from CreateFymSequence import create_fym_sequence
        FYM_sequence = create_fym_sequence(crop_sequence,FYM_mean_per_rot)
    
    #Create climate sequence 
    from BuildClimateSequence import build_climate_sequence_from_calendar
    temperature_sequence = build_climate_sequence_from_calendar(
        crop_calendar=crop_calendar,
        climate_df=monthly_temp_df,
        variable_name='Temperature_C'
    )
    temperature_sequence = pd.Series(temperature_sequence, name='T')

    precipitation_sequence = build_climate_sequence_from_calendar(
        crop_calendar=crop_calendar,
        climate_df=monthly_pr_df,
        variable_name='Precipitation_mm'
    )
    precipitation_sequence = pd.Series(precipitation_sequence, name='P')

    humidity_sequence = build_climate_sequence_from_calendar(
        crop_calendar=crop_calendar,
        climate_df=monthly_rh_df,
        variable_name='RelHumidity_%'
    )
    humidity_sequence = pd.Series(humidity_sequence, name='RH')

    radiation_sequence = build_climate_sequence_from_calendar(
        crop_calendar=crop_calendar,
        climate_df=monthly_rn_df,
        variable_name='NetRad_Wm-2'
    )
    radiation_sequence = pd.Series(radiation_sequence, name='Rn')


    #Calculate PET from these climate variables
    from CalculatePETPM import calculate_pet_penman_monteith
    pet_sequence = calculate_pet_penman_monteith(
        temp_c=temperature_sequence,
        rh_percent=humidity_sequence,
        shortwave_rad=radiation_sequence,  # your shortwave radiation data
        month_series=None,
        latitude=50.56  # Gembloux latitude
    )
    
    DataRothC = pd.DataFrame({
        "T": temperature_sequence,
        "Evap": pet_sequence,
        "P": precipitation_sequence,
        "FYM": FYM_sequence,        
        "AGB": AGB_sequence,      
        "SoilCover": soilcover_sequence,
        "Crop": crop_sequence
    })
    DataRothC.to_csv(os.path.join(os.path.join(data_path, f'DataRothCRun_{management_scenario}_{warming_scenario}_{straw_scenario}.csv')))
   
    return DataRothC