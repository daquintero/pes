import numpy as np
from piel.types import MultiTimeSignalData, TimeSignalData


def offset_time_signals(multi_signal: MultiTimeSignalData) -> MultiTimeSignalData:
    """
    Offsets the time_s array of each TimeSignalData in the MultiTimeSignalData to start at 0.

    Args:
        multi_signal (MultiTimeSignalData): List of rising edge signals.

    Returns:
        MultiTimeSignalData: New list with offset time_s arrays.
    """
    offset_signals = []
    for signal in multi_signal:
        if not signal.time_s:
            raise ValueError(f"Signal '{signal.data_name}' has an empty time_s array.")

        # Convert to numpy arrays for efficient computation
        time = np.array(signal.time_s)
        data = np.array(signal.data)

        # Calculate the offset (start time)
        offset = time[0]

        # Apply the offset
        offset_time = time - offset

        # Create a new TimeSignalData instance with the offset time
        offset_signal = TimeSignalData(
            time_s=offset_time.tolist(), data=data.tolist(), data_name=signal.data_name
        )
        offset_signals.append(offset_signal)

    return offset_signals
