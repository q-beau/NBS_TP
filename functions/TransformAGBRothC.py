# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 09:53:46 2025

@author: u230231
"""
import numpy as np
import pandas as pd


def transform_agb_rothc(series):
    """Distribute block values: last element 1/2, three preceding elements 1/6 each."""
    values = series.to_numpy(dtype=float, copy=True)  # writable copy

    i = 0
    while i < len(values):
        if np.isnan(values[i]) or values[i] == 0:
            i += 1
            continue

        # end of block of identical values
        j = i
        while j + 1 < len(values) and values[j + 1] == values[i]:
            j += 1

        block_value = values[i]
        values[i:j + 1] = 0.0
        values[j] = block_value / 2.0
        for k in range(max(i, j - 3), j):
            values[k] = block_value / 6.0

        i = j + 1

    return pd.Series(values, index=series.index, name=series.name).fillna(0)