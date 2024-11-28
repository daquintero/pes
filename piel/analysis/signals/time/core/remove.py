from piel.types import TimeSignalData
import numpy as np


def remove_before_first_rising_edge(
    waveform: TimeSignalData,
    lower_threshold_ratio: float = 0.1,
    upper_threshold_ratio: float = 0.9,
) -> TimeSignalData:
    """
    Removes all data points before the first rising edge in the waveform.

    A rising edge is defined as the point where the signal transitions from below the lower
    threshold to above the upper threshold.

    Parameters:
        waveform (TimeSignalData): The input waveform data.
        lower_threshold_ratio (float): Lower threshold as a ratio of the amplitude range.
        upper_threshold_ratio (float): Upper threshold as a ratio of the amplitude range.

    Returns:
        TimeSignalData: A new waveform with data points before the first rising edge removed.

    Raises:
        ValueError: If no rising edge is found in the waveform.
    """
    # Convert time and data to numpy arrays for efficient computation
    time = np.array(waveform.time_s)
    data = np.array(waveform.data)

    # Validate input lengths
    if len(time) != len(data):
        raise ValueError("Time and data arrays must have the same length.")

    # Calculate amplitude range
    data_min = np.min(data)
    data_max = np.max(data)
    amplitude_range = data_max - data_min

    if amplitude_range == 0:
        raise ValueError("Signal has zero amplitude range; cannot detect rising edge.")

    # Define thresholds based on the amplitude range
    lower_threshold = data_min + amplitude_range * lower_threshold_ratio
    upper_threshold = data_min + amplitude_range * upper_threshold_ratio

    # Identify indices where signal crosses the lower threshold
    below_lower = data < lower_threshold
    above_lower = data >= lower_threshold
    # Detect transitions from below_lower to above_lower
    rising_cross_lower = np.where(below_lower[:-1] & above_lower[1:])[0] + 1

    # Iterate through potential rising edges to find the first that crosses the upper threshold
    rising_edge_idx = None
    for idx in rising_cross_lower:
        if data[idx] >= upper_threshold:
            rising_edge_idx = idx
            break
        # Alternatively, find the exact crossing point using interpolation
        crossing_indices = np.where(data[idx:] >= upper_threshold)[0]
        if crossing_indices.size > 0:
            rising_edge_idx = idx + crossing_indices[0]
            break

    if rising_edge_idx is None:
        raise ValueError("No rising edge found that crosses the specified thresholds.")

    # Slice the time and data arrays from the rising edge onwards
    sliced_time = time[rising_edge_idx:]
    sliced_data = data[rising_edge_idx:]

    # Optionally, reset the time so that the rising edge starts at zero
    sliced_time = sliced_time - sliced_time[0]

    # Create a new TimeSignalData instance with the sliced data
    trimmed_signal = TimeSignalData(
        time_s=sliced_time.tolist(),
        data=sliced_data.tolist(),
        data_name=waveform.data_name,
    )

    return trimmed_signal
