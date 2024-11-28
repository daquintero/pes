import numpy as np
from typing import Callable, Optional, Dict
from piel.types import (
    TimeSignalData,
)  # Ensure this import matches your project structure


# Existing create_off_state_generator function
def create_off_state_generator(
    noise_std: float = 0.01,
    sampling_rate: float = 1000.0,
    baseline: float = 0.0,
    data_name: str = "off_state",
    data_time_signal_kwargs: Optional[Dict] = None,
) -> Callable[[float, Optional[int]], TimeSignalData]:
    """
    Creates a generator function for the equivalent off state signal with noise.

    Parameters:
        noise_std (float): Standard deviation of the Gaussian noise.
        sampling_rate (float): Sampling rate in Hz.
        baseline (float): Baseline signal level for the off state.
        data_name (str): Name of the data signal.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for TimeSignalData.

    Returns:
        Callable[[float, Optional[int]], TimeSignalData]:
            A function that takes duration_s (in seconds) and returns TimeSignalData.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    def generate_off_state(
        duration_s: float, num_samples: Optional[int] = None
    ) -> TimeSignalData:
        """
        Generates the off state signal data with noise for a given duration_s.

        Parameters:
            duration_s (float): Duration of the signal in seconds.
            num_samples (float): Number of samples to generate.

        Returns:
            TimeSignalData: The generated signal data.
        """
        if num_samples is None:
            num_samples = int(duration_s * sampling_rate)
        time_s = np.linspace(0, duration_s, num_samples, endpoint=False)
        noise = np.random.normal(loc=0.0, scale=noise_std, size=num_samples)
        data = baseline + noise

        return TimeSignalData(
            time_s=time_s.tolist(),
            data=data.tolist(),
            data_name=data_name,
            **data_time_signal_kwargs,
        )

    return generate_off_state


# New function to extract parameters and create generator
def extract_off_state_generator_from_off_state_section(
    off_state_data: TimeSignalData,
    data_name: Optional[str] = None,
    data_time_signal_kwargs: Optional[Dict] = None,
) -> Callable[[float], TimeSignalData]:
    """
    Extracts parameters from an existing off state DataTimeSignalData and creates a generator function.

    Parameters:
        off_state_data (TimeSignalData): The existing off state signal data.
        data_name (str, optional): Name for the new data signal. Defaults to the original data_name.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.

    Returns:
        Callable[[float], DataTimeSignalData]:
            A generator function configured with extracted parameters.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    # Extract baseline as the mean of the data
    baseline = np.mean(off_state_data.data)

    # Extract noise standard deviation as the standard deviation of the data
    noise_std = np.std(off_state_data.data)

    # Extract sampling rate from time_s array
    if len(off_state_data.time_s) < 2:
        raise ValueError(
            "time_s array must contain at least two elements to calculate sampling rate."
        )

    # Calculate the sampling interval (assuming uniform sampling)
    sampling_intervals = np.diff(off_state_data.time_s)
    mean_sampling_interval = np.mean(sampling_intervals)
    sampling_rate = 1.0 / mean_sampling_interval

    # Use the provided data_name or default to the original
    new_data_name = data_name if data_name is not None else off_state_data.data_name

    # Optionally, pass through units or other kwargs
    # For example, override units if provided in data_time_signal_kwargs
    return create_off_state_generator(
        noise_std=noise_std,
        sampling_rate=sampling_rate,
        baseline=baseline,
        data_name=new_data_name,
        data_time_signal_kwargs=data_time_signal_kwargs,
    )


def extract_off_state_generator_from_full_state_data(
    full_time_signal_data: TimeSignalData,
    baseline: Optional[float] = None,
    threshold: Optional[float] = None,
    min_duration_s: Optional[float] = None,
    sampling_rate: Optional[float] = None,
    data_name: Optional[str] = None,
    data_time_signal_kwargs: Optional[Dict] = None,
) -> Callable[[float, Optional[int]], TimeSignalData]:
    """
    Extracts parameters from an existing off state DataTimeSignalData and creates a generator function.

    Parameters:
        full_time_signal_data (TimeSignalData): The input signal data containing multiple states.
        baseline (float, optional): The baseline value representing the off state.
                                     If not provided, it is computed as the mean of the data.
        threshold (float, optional): The maximum deviation from the baseline to consider as off state.
                                     If not provided, it is computed as 2 * standard deviation of the data.
        min_duration_s (float, optional): The minimum duration_s (in seconds) for a segment to be considered.
                                        Segments shorter than this duration_s will be ignored.
        sampling_rate (float, optional): The sampling rate in Hz. If not provided, it is calculated from time_s.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.
        data_name (str, optional): Name for the new data signal. Defaults to the original data_name.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.

    Returns:
        Callable[[float], DataTimeSignalData]:
            A generator function configured with extracted parameters.
    """

    off_state_data = extract_off_state_section(
        full_time_signal_data=full_time_signal_data,
        baseline=baseline,
        threshold=threshold,
        min_duration_s=min_duration_s,
        sampling_rate=sampling_rate,
    )

    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    # Extract baseline as the mean of the data
    baseline = np.mean(off_state_data.data)

    # Extract noise standard deviation as the standard deviation of the data
    noise_std = np.std(off_state_data.data)

    # Extract sampling rate from time_s array
    if len(off_state_data.time_s) < 2:
        raise ValueError(
            "time_s array must contain at least two elements to calculate sampling rate."
        )

    # Calculate the sampling interval (assuming uniform sampling)
    sampling_intervals = np.diff(off_state_data.time_s)
    mean_sampling_interval = np.mean(sampling_intervals)
    sampling_rate = 1.0 / mean_sampling_interval

    # Use the provided data_name or default to the original
    new_data_name = data_name if data_name is not None else off_state_data.data_name

    # Optionally, pass through units or other kwargs
    # For example, override units if provided in data_time_signal_kwargs
    return create_off_state_generator(
        noise_std=noise_std,
        sampling_rate=sampling_rate,
        baseline=baseline,
        data_name=new_data_name,
        data_time_signal_kwargs=data_time_signal_kwargs,
    )


def extract_off_state_section(
    full_time_signal_data: TimeSignalData,
    baseline: Optional[float] = None,
    threshold: Optional[float] = None,
    min_duration_s: Optional[float] = None,
    sampling_rate: Optional[float] = None,
    data_time_signal_kwargs: Optional[Dict] = None,
) -> TimeSignalData:
    """
    Extracts the off state segments from a DataTimeSignalData instance containing multiple on and off states.

    Parameters:
        full_time_signal_data (TimeSignalData): The input signal data containing multiple states.
        baseline (float, optional): The baseline value representing the off state.
                                     If not provided, it is computed as the mean of the data.
        threshold (float, optional): The maximum deviation from the baseline to consider as off state.
                                     If not provided, it is computed as 2 * standard deviation of the data.
        min_duration_s (float, optional): The minimum duration_s (in seconds) for a segment to be considered.
                                        Segments shorter than this duration_s will be ignored.
        sampling_rate (float, optional): The sampling rate in Hz. If not provided, it is calculated from time_s.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.

    Returns:
        TimeSignalData: A new DataTimeSignalData instance containing only the off state segments.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    data = np.array(full_time_signal_data.data)
    time_s = np.array(full_time_signal_data.time_s)

    # Compute baseline if not provided
    if baseline is None:
        baseline = np.mean(data)

    # Compute threshold if not provided
    if threshold is None:
        threshold = 2 * np.std(data)

    # Determine sampling rate if not provided
    if sampling_rate is None:
        if len(time_s) < 2:
            raise ValueError(
                "time_s array must contain at least two elements to calculate sampling rate."
            )
        sampling_intervals = np.diff(time_s)
        mean_sampling_interval = np.mean(sampling_intervals)
        sampling_rate = 1.0 / mean_sampling_interval

    # Identify points within the threshold around the baseline
    off_state_mask = np.abs(data - baseline) <= threshold

    # Find continuous segments where off_state_mask is True
    off_state_indices = np.where(off_state_mask)[0]

    if off_state_indices.size == 0:
        raise ValueError("No off state segments found based on the provided criteria.")

    # Group consecutive indices
    segments: list[list[int]] = []
    current_segment = [off_state_indices[0]]

    for idx in off_state_indices[1:]:
        if idx == current_segment[-1] + 1:
            current_segment.append(idx)
        else:
            segments.append(current_segment)
            current_segment = [idx]
    segments.append(current_segment)  # Add the last segment

    # Filter segments by min_duration_s if specified
    if min_duration_s is not None:
        min_samples = int(min_duration_s * sampling_rate)
        segments = [seg for seg in segments if len(seg) >= min_samples]

    if not segments:
        raise ValueError(
            "No off state segments meet the minimum duration_s requirement."
        )

    # Concatenate all segments
    extracted_time = []
    extracted_data = []

    for seg in segments:
        extracted_time.extend(time_s[seg])
        extracted_data.extend(data[seg])

    # Optionally, sort the extracted data by time
    sorted_indices = np.argsort(extracted_time)
    extracted_time = np.array(extracted_time)[sorted_indices].tolist()
    extracted_data = np.array(extracted_data)[sorted_indices].tolist()

    # Create a new TimeSignalData instance
    extracted_off_state = TimeSignalData(
        time_s=extracted_time,
        data=extracted_data,
        data_name=full_time_signal_data.data_name + "_off_state",
        **data_time_signal_kwargs,
    )

    return extracted_off_state
