# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:14:28 2025

@author: qbeau
"""

# Define exact mappings for scenario components
def get_expected_labels(key):
    parts = key.split('_')
    ws_part = parts[0]      # '2.6'
    rot_part = parts[1]    # 'baseline'  
    sr_part = parts[2]      # '50'

    expected_labels = [
        f'WS {ws_part}',                    # 'WS 2.6'
        f'{rot_part}',         # 'ecofood_ref' (exact)
        f'SR {sr_part}'                     # 'SR 50'
    ]
    return expected_labels