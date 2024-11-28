import numpy as np
from piel.types import TimeSignalData


def offset_to_first_rising_edge(
    waveform: TimeSignalData,
    lower_threshold_ratio: float = 0.1,
    upper_threshold_ratio: float = 0.9,
) -> TimeSignalData:
    """
    Offsets the waveform's time axis so that the first rising edge occurs at time zero.

    A rising edge is defined as the point where the signal transitions from below the lower
    threshold to above the upper threshold.

    Parameters:
        waveform (TimeSignalData): The input waveform data.
        lower_threshold_ratio (float): Lower threshold as a ratio of the amplitude range.
        upper_threshold_ratio (float): Upper threshold as a ratio of the amplitude range.

    Returns:
        TimeSignalData: A new waveform with the time offset applied.

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
    # above_lower = data >= lower_threshold
    rising_cross_lower = np.where(~below_lower[:-1] & below_lower[1:])[0] + 1

    # Iterate through potential rising edges to find the first that crosses the upper threshold
    for idx in rising_cross_lower:
        # Check if subsequent data points cross the upper threshold
        if data[idx] >= upper_threshold:
            offset_time = time[idx]
            break
        # Alternatively, find the exact crossing point using interpolation
        # Find where the signal crosses the upper threshold after the lower threshold
        crossing_indices = np.where(data[idx:] >= upper_threshold)[0]
        if crossing_indices.size > 0:
            crossing_idx = idx + crossing_indices[0]
            offset_time = time[crossing_idx]
            break
    else:
        raise ValueError("No rising edge found that crosses the specified thresholds.")

    # Apply the offset
    offset_time_array = time - offset_time

    # Create a new TimeSignalData instance with the offset time
    offset_signal = TimeSignalData(
        time_s=offset_time_array.tolist(),
        data=data.tolist(),
        data_name=waveform.data_name,
    )

    return offset_signal
