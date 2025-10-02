import pandas as pd

def create_fym_sequence(crop_sequence, fym_mean, target_crop=7.0):
    """
    Create FYM (Farm Yard Manure) sequence based on crop sequence.
    Adds fym_mean after the 2nd, 4th, 6th... occurrences of target_crop blocks.
    
    Parameters:
    - crop_sequence: list, array, or pandas Series of crop codes
    - fym_mean: value to add for FYM application (e.g., manure amount)
    - target_crop: crop code to track for FYM application (default 7.0)
    
    Returns:
    - fym_sequence: pandas Series of FYM values (0 or fym_mean)
    """
    
    # Convert to pandas Series if not already
    if not isinstance(crop_sequence, pd.Series):
        crop_sequence = pd.Series(crop_sequence)
    
    # Initialize FYM sequence with zeros, preserving the original index
    fym_sequence = pd.Series([0.0] * len(crop_sequence), index=crop_sequence.index)
    
    # Find blocks of consecutive target_crop values
    crop_blocks = []
    i = 0
    crop_values = crop_sequence.values
    
    while i < len(crop_values):
        if crop_values[i] == target_crop:
            # Found start of a block
            block_start = i
            # Find end of block
            while i < len(crop_values) and crop_values[i] == target_crop:
                i += 1
            block_end = i - 1
            crop_blocks.append((block_start, block_end))
        else:
            i += 1
    
    # Apply FYM after even-numbered blocks (2nd, 4th, 6th, ...)
    for block_idx, (block_start, block_end) in enumerate(crop_blocks):
        block_number = block_idx + 1  # 1-indexed
        
        if block_number % 2 == 0:  # Even block numbers (2, 4, 6, ...)
            # Apply FYM at the end of the block using original index
            original_index = crop_sequence.index[block_end]
            fym_sequence.loc[original_index] = fym_mean
    
    return fym_sequence

# Example usage:
# If crop_sequence is already a Series:
# fym_sequence = create_fym_sequence(crop_sequence, fym_mean=10.0)

# If crop_sequence is a list or array:
# fym_sequence = create_fym_sequence(crop_list, fym_mean=10.0)
