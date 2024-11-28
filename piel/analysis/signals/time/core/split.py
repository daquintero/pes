# separate_pulse_thresholds.py
import numpy as np
from typing import List, Optional, Dict
from piel.types import (
    TimeSignalData,
    MultiTimeSignalData,
)  # Adjust the import path as needed
from .threshold import (
    extract_pulses_from_signal,
    is_pulse_above_threshold,
)  # Ensure this import path is correct
from .compose import compose_pulses_into_signal


def separate_per_pulse_threshold(
    signal_data: TimeSignalData,
    first_signal_threshold: float,
    second_signal_threshold: float,
    trigger_delay_s: float,
    trigger_window_s: float = 25e-9,
    first_pre_pulse_time_s: float = 1e-9,
    first_post_pulse_time_s: float = 1e-9,
    second_pre_pulse_time_s: float = 1e-9,
    second_post_pulse_time_s: float = 1e-9,
    noise_std_multiplier: float = 3.0,
    data_time_signal_kwargs: Optional[Dict] = None,
) -> List[MultiTimeSignalData]:
    """
    Separates pulses in a signal into two categories based on two threshold values.

    Parameters:
        signal_data (TimeSignalData): The input signal data containing multiple pulses.
        first_signal_threshold (float): The higher threshold to categorize pulses.
        second_signal_threshold (float): The lower threshold to categorize pulses.
        trigger_delay_s (float): Minimum time (in seconds) between pulses to prevent overlap.
        first_pre_pulse_time_s (float, optional): Time (in seconds) to include before each detected pulse.
                                           Defaults to 0.01.
        first_post_pulse_time_s (float, optional): Time (in seconds) to include after each detected pulse.
                                            Defaults to 0.01.\
        second_pre_pulse_time_s (float, optional): Time (in seconds) to include before each detected pulse.
                                           Defaults to 0.01.
        second_post_pulse_time_s (float, optional): Time (in seconds) to include after each detected pulse.
                                            Defaults to 0.01.
        noise_std_multiplier (float, optional): Multiplier for noise standard deviation to set detection threshold.
                                                Defaults to 3.0.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.

    Returns:
        List[MultiTimeSignalData]: A list containing a single `MultiTimeSignalData` instance:
            - `high_threshold_pulses`: List of `DataTimeSignalData` for pulses above `first_signal_threshold`.
            - `low_threshold_pulses`: List of `DataTimeSignalData` for pulses above `second_signal_threshold` but below `first_signal_threshold`.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    # Ensure thresholds are valid
    if second_signal_threshold >= first_signal_threshold:
        raise ValueError(
            "second_signal_threshold must be less than first_signal_threshold."
        )

    # Extract high-threshold pulses
    high_threshold_pulses = extract_pulses_from_signal(
        full_data=signal_data,
        pre_pulse_time_s=first_pre_pulse_time_s,
        post_pulse_time_s=first_post_pulse_time_s,
        noise_std_multiplier=noise_std_multiplier,
        min_pulse_height=first_signal_threshold,
        data_time_signal_kwargs=data_time_signal_kwargs,
    )

    # Extract low-threshold pulses
    low_threshold_pulses = extract_pulses_from_signal(
        full_data=signal_data,
        pre_pulse_time_s=second_pre_pulse_time_s,
        post_pulse_time_s=second_post_pulse_time_s,
        noise_std_multiplier=noise_std_multiplier,
        min_pulse_height=second_signal_threshold,
        data_time_signal_kwargs=data_time_signal_kwargs,
    )

    # Filter low-threshold pulses by excluding those that exceed the first_signal_threshold
    filtered_low_threshold_pulses = [
        pulse
        for pulse in low_threshold_pulses
        if not is_pulse_above_threshold(pulse, first_signal_threshold)
    ]

    # Function to find the peak time of a pulse
    def get_pulse_peak_time(pulse: TimeSignalData) -> float:
        if not pulse.data or not pulse.time_s:
            return float("inf")  # Assign a large value if pulse data is empty
        max_idx = np.argmax(pulse.data)
        return pulse.time_s[max_idx]

    # Get peak times for all high threshold pulses
    high_pulse_peak_times = [
        get_pulse_peak_time(pulse) for pulse in high_threshold_pulses
    ]

    # Filter low_threshold_pulses to ensure they are at least `trigger_delay_s` away from any high_threshold_pulse
    filtered_low_threshold_pulses = []
    for low_pulse in low_threshold_pulses:
        low_pulse_peak_time = get_pulse_peak_time(low_pulse)
        # print("low")
        # print(low_pulse_peak_time)
        # Check distance from all high pulse peaks
        for high_peak in high_pulse_peak_times:
            # print("high")
            # print(high_peak)
            # print("diff")
            # print(abs(high_peak - low_pulse_peak_time))
            if (
                (abs(low_pulse_peak_time - high_peak) > trigger_delay_s)
                and (high_peak < low_pulse_peak_time)
                and (high_peak > low_pulse_peak_time - trigger_window_s)
            ):
                filtered_low_threshold_pulses.append(low_pulse)
                # print(True)

    # Additionally, ensure that low_threshold_pulses do not exceed the first_signal_threshold
    # This is to categorize pulses exclusively
    final_low_threshold_pulses = [
        pulse
        for pulse in filtered_low_threshold_pulses
        if not is_pulse_above_threshold(pulse, first_signal_threshold)
    ]

    return [high_threshold_pulses, final_low_threshold_pulses]


def split_compose_per_pulse_threshold(
    signal_data: TimeSignalData,
    first_signal_threshold: float,
    second_signal_threshold: float,
    trigger_delay_s: float,
    first_pre_pulse_time_s: float = 1e-9,
    first_post_pulse_time_s: float = 1e-9,
    second_pre_pulse_time_s: float = 1e-9,
    second_post_pulse_time_s: float = 1e-9,
    noise_std_multiplier: float = 3.0,
    start_time_s: Optional[float] = None,
    end_time_s: Optional[float] = None,
    data_time_signal_kwargs: Optional[Dict] = None,
) -> MultiTimeSignalData:
    """
    Separates pulses in a signal into two categories based on two threshold values.

    Parameters:
        signal_data (TimeSignalData): The input signal data containing multiple pulses.
        first_signal_threshold (float): The higher threshold to categorize pulses.
        second_signal_threshold (float): The lower threshold to categorize pulses.
        trigger_delay_s (float): Minimum time (in seconds) between pulses to prevent overlap.
        first_pre_pulse_time_s (float, optional): Time (in seconds) to include before each detected first pulse.
                                           Defaults to 0.01.
        first_post_pulse_time_s (float, optional): Time (in seconds) to include after each detected first pulse.
                                            Defaults to 0.01.
        second_pre_pulse_time_s (float, optional): Time (in seconds) to include before each detected second pulse.
                                           Defaults to 0.01.
        second_post_pulse_time_s (float, optional): Time (in seconds) to include after each detected second pulse.
                                            Defaults to 0.01.
        noise_std_multiplier (float, optional): Multiplier for noise standard deviation to set detection threshold.
                                                Defaults to 3.0.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.
        start_time_s (float, optional): Start time of the composed signal. If not provided, uses the first pulse's start time.
        end_time_s (float, optional): End time of the composed signal. If not provided, uses the last pulse's end time.

    Returns:
        List[TimeSignalData]: The composed full signals as [low_threshold_pulse_signal, high_threshold_pulse_signal]
    """

    high_threshold_pulse_list, low_threshold_pulse_list = separate_per_pulse_threshold(
        signal_data=signal_data,
        first_signal_threshold=first_signal_threshold,
        second_signal_threshold=second_signal_threshold,
        trigger_delay_s=trigger_delay_s,
        first_pre_pulse_time_s=first_pre_pulse_time_s,
        first_post_pulse_time_s=first_post_pulse_time_s,
        second_post_pulse_time_s=second_post_pulse_time_s,
        second_pre_pulse_time_s=second_pre_pulse_time_s,
        noise_std_multiplier=noise_std_multiplier,
        data_time_signal_kwargs=data_time_signal_kwargs,
    )

    low_threshold_pulse_signal = compose_pulses_into_signal(
        low_threshold_pulse_list,
        start_time_s=start_time_s,
        end_time_s=end_time_s,
    )
    high_threshold_pulse_signal = compose_pulses_into_signal(
        high_threshold_pulse_list,
        start_time_s=start_time_s,
        end_time_s=end_time_s,
    )
    return [low_threshold_pulse_signal, high_threshold_pulse_signal]
