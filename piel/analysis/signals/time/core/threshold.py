import numpy as np
from scipy.signal import find_peaks
from piel.types import TimeSignalData, MultiTimeSignalData
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def extract_signal_above_threshold(
    signal_data: TimeSignalData,
    threshold: float,
    min_pulse_width_s: float = 0.0,
    noise_floor: float = 0.0,
) -> MultiTimeSignalData:
    """
    Extracts all pulses from the input signal that exceed the specified threshold.

    Args:
        signal_data (TimeSignalData): The original signal data containing time and data arrays.
        threshold (float): The data value threshold to identify pulses.
        min_pulse_width_s (float, optional): The minimum duration (in seconds) for a pulse to be considered valid.
                                             Pulses shorter than this duration will be ignored. Defaults to 0.0.
        noise_floor (float, optional): The value to assign to non-pulse regions in the extracted pulses.
                                       Defaults to 0.0.

    Returns:
        MultiTimeSignalData: A list of DataTimeSignalData instances, each representing a detected pulse.
    """
    # Convert lists to NumPy arrays for efficient processing
    time = np.array(signal_data.time_s)
    data = np.array(signal_data.data)

    if len(time) != len(data):
        raise ValueError("Time and data arrays must have the same length.")

    # Identify where data exceeds the threshold
    above_threshold = data > threshold

    # Find rising and falling edges
    edges = np.diff(above_threshold.astype(int))
    pulse_start_indices = (
        np.where(edges == 1)[0] + 1
    )  # +1 to correct the index after diff
    pulse_end_indices = np.where(edges == -1)[0] + 1

    # Handle edge cases where the signal starts or ends above the threshold
    if above_threshold[0]:
        pulse_start_indices = np.insert(pulse_start_indices, 0, 0)
    if above_threshold[-1]:
        pulse_end_indices = np.append(pulse_end_indices, len(data))

    logger.debug(f"Detected {len(pulse_start_indices)} potential pulses.")

    # Initialize list to hold extracted pulses
    extracted_pulses: MultiTimeSignalData = []

    # Iterate over each detected pulse
    for idx, (start_idx, end_idx) in enumerate(
        zip(pulse_start_indices, pulse_end_indices), start=1
    ):
        pulse_duration = time[end_idx - 1] - time[start_idx]

        if pulse_duration < min_pulse_width_s:
            logger.debug(
                f"Pulse {idx} ignored due to insufficient width: {pulse_duration}s < {min_pulse_width_s}s."
            )
            continue  # Skip pulses that are too short

        # Extract the pulse time and data
        pulse_time = time[start_idx:end_idx]
        pulse_data = data[start_idx:end_idx]

        # Optionally, assign noise_floor to non-pulse regions if maintaining original array length
        # Here, we create pulses with their own time and data arrays

        # Create a TimeSignalData instance for the pulse
        pulse_signal = TimeSignalData(
            time_s=pulse_time.tolist(),
            data=pulse_data.tolist(),
            data_name=f"{signal_data.data_name}_pulse_{idx}",
        )

        extracted_pulses.append(pulse_signal)

        logger.debug(
            f"Pulse {idx} extracted: Start={time[start_idx]}s, End={time[end_idx - 1]}s, Duration={pulse_duration}s."
        )

    logger.info(f"Total pulses extracted: {len(extracted_pulses)}.")

    return extracted_pulses


def extract_pulses_from_signal(
    full_data: TimeSignalData,
    pre_pulse_time_s: float = 0.01,
    post_pulse_time_s: float = 0.01,
    noise_std_multiplier: float = 3.0,
    min_pulse_height: Optional[float] = None,
    min_pulse_distance_s: Optional[float] = None,
    data_time_signal_kwargs: Optional[dict] = None,
) -> List[TimeSignalData]:
    """
    Detects and extracts pulses from a DataTimeSignalData instance, including segments
    before and after each pulse up to the noise floor.

    Parameters:
        full_data (TimeSignalData): The input signal data containing multiple pulses.
        pre_pulse_time_s (float): Time (in seconds) to include before each detected pulse.
        post_pulse_time_s (float): Time (in seconds) to include after each detected pulse.
        noise_std_multiplier (float): Multiplier for noise standard deviation to set detection threshold.
        min_pulse_height (float, optional): Minimum height of a pulse to be detected. If not provided,
                                            it is set to noise_std_multiplier * noise_std.
        min_pulse_distance_s (float, optional): Minimum distance (in seconds) between consecutive pulses.
                                              If not provided, it is set based on the pre_pulse_time and post_pulse_time.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.

    Returns:
        List[TimeSignalData]: A list of DataTimeSignalData instances, each representing an extracted pulse.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    data = np.array(full_data.data)
    time_s = np.array(full_data.time_s)

    if len(time_s) != len(data):
        raise ValueError("time_s and data must have the same length.")

    # Compute baseline and noise statistics
    baseline = np.mean(data)
    noise_std = np.std(data)

    # Set detection threshold
    if min_pulse_height is None:
        detection_threshold = baseline + noise_std_multiplier * noise_std
    else:
        detection_threshold = min_pulse_height

    # Determine sampling rate
    if len(time_s) < 2:
        raise ValueError(
            "time_s array must contain at least two elements to calculate sampling rate."
        )
    sampling_intervals = np.diff(time_s)
    mean_sampling_interval = np.mean(sampling_intervals)
    sampling_rate = 1.0 / mean_sampling_interval

    # Set minimum distance between pulses
    if min_pulse_distance_s is None:
        # Minimum distance in samples based on pre and post pulse time
        min_pulse_distance_s = (pre_pulse_time_s + post_pulse_time_s) * sampling_rate

    else:
        # Convert distance from seconds to samples
        min_pulse_distance_s = min_pulse_distance_s * sampling_rate

    # Detect peaks
    peaks, properties = find_peaks(
        data,
        height=detection_threshold,
        distance=min_pulse_distance_s,
    )

    if len(peaks) == 0:
        raise ValueError("No pulses detected based on the provided criteria.")

    extracted_pulses = []

    for peak_idx in peaks:
        # Define window around the peak
        peak_time = time_s[peak_idx]

        # Determine pre-pulse start time
        pre_start_time = peak_time - pre_pulse_time_s
        pre_start_time = max(pre_start_time, time_s[0])

        # Determine post-pulse end time
        post_end_time = peak_time + post_pulse_time_s
        post_end_time = min(post_end_time, time_s[-1])

        # Find indices corresponding to pre_start_time and post_end_time
        pre_start_idx = np.searchsorted(time_s, pre_start_time, side="left")
        post_end_idx = np.searchsorted(time_s, post_end_time, side="right")

        # Extract the segment
        segment_time = time_s[pre_start_idx:post_end_idx]
        segment_data = data[pre_start_idx:post_end_idx]

        # Create a new TimeSignalData instance for the pulse
        pulse_data_name = f"{full_data.data_name}_pulse_{peak_idx}"
        extracted_pulse = TimeSignalData(
            time_s=segment_time.tolist(),
            data=segment_data.tolist(),
            data_name=pulse_data_name,
            **data_time_signal_kwargs,
        )

        extracted_pulses.append(extracted_pulse)

    return extracted_pulses


def is_pulse_above_threshold(pulse: TimeSignalData, threshold: float) -> bool:
    """
    Determines if the pulse's amplitude exceeds the specified threshold.

    Parameters:
        pulse (TimeSignalData): The pulse data to evaluate.
        threshold (float): The amplitude threshold.

    Returns:
        bool: True if the pulse's maximum amplitude is greater than or equal to the threshold, False otherwise.
    """
    if not pulse.data:
        return False
    max_amplitude = max(pulse.data)
    return max_amplitude >= threshold
