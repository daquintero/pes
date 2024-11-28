import numpy as np
from piel.types import TimeSignalData, MultiTimeSignalData


def extract_rising_edges(
    signal: TimeSignalData,
    lower_threshold_ratio: float = 0.1,
    upper_threshold_ratio: float = 0.9,
) -> MultiTimeSignalData:
    """
    Extracts rising edges from a signal defined as transitions from lower_threshold to upper_threshold.

    Args:
        signal (TimeSignalData): The input signal data.
        lower_threshold_ratio (float): Lower threshold as a fraction of signal amplitude (default 0.1).
        upper_threshold_ratio (float): Upper threshold as a fraction of signal amplitude (default 0.9).

    Returns:
        MultiTimeSignalData: A list of DataTimeSignalData instances, each representing a rising edge.
    """
    # Convert lists to numpy arrays for efficient processing
    time = np.array(signal.time_s)
    data = np.array(signal.data)

    if len(time) != len(data):
        raise ValueError("time_s and data must be of the same length.")

    # Determine signal amplitude range
    data_min = np.min(data)
    data_max = np.max(data)
    amplitude = data_max - data_min

    # Calculate absolute threshold values
    lower_threshold = data_min + lower_threshold_ratio * amplitude
    upper_threshold = data_min + upper_threshold_ratio * amplitude

    # Initialize list to hold rising edges
    rising_edges: MultiTimeSignalData = []

    # State variables
    in_rising = False
    start_idx = None

    for i in range(1, len(data)):
        # Detect transition from below lower_threshold to above lower_threshold
        if not in_rising:
            if data[i - 1] < lower_threshold and data[i] >= lower_threshold:
                start_idx = i - 1  # Potential start of rising edge
                in_rising = True
        else:
            # Check if signal has reached upper_threshold
            if data[i] >= upper_threshold:
                end_idx = i
                # Extract the segment corresponding to the rising edge
                edge_time = time[start_idx : end_idx + 1]
                edge_data = data[start_idx : end_idx + 1]

                # Create a new TimeSignalData instance for the rising edge
                edge_signal = TimeSignalData(
                    time_s=edge_time.tolist(),
                    data=edge_data.tolist(),
                    data_name=f"{signal.data_name}_rising_edge_{len(rising_edges) + 1}",
                )
                rising_edges.append(edge_signal)

                # Reset state
                in_rising = False
                start_idx = None
            elif data[i] < lower_threshold:
                # False alarm, reset state
                in_rising = False
                start_idx = None

    return rising_edges
