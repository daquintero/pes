# compose_pulses.py

import numpy as np
from typing import List, Optional
from piel.types import TimeSignalData
from .off_state import (
    extract_off_state_generator_from_full_state_data,
)  # Adjust the import path as needed


def compose_pulses_into_signal(
    pulses: List[TimeSignalData],
    baseline: float = 0.0,
    noise_std: Optional[float] = None,
    data_time_signal_kwargs: Optional[dict] = None,
    start_time_s: Optional[float] = None,
    end_time_s: Optional[float] = None,
) -> TimeSignalData:
    """
    Composes a full signal from a list of pulses by inserting them into a continuous time array
    and filling gaps with generated noise.

    Parameters:
        pulses (List[TimeSignalData]): List of pulse signals to be inserted.
        baseline (float, optional): Baseline value of the signal. Defaults to 0.0.
        noise_std (float, optional): Standard deviation of the noise to be generated in gaps.
                                     If not provided, it is estimated from the pulses.
        data_time_signal_kwargs (dict, optional): Additional keyword arguments for DataTimeSignalData.
        start_time_s (float, optional): Start time of the composed signal. If not provided, uses the first pulse's start time.
        end_time_s (float, optional): End time of the composed signal. If not provided, uses the last pulse's end time.

    Returns:
        TimeSignalData: The composed full signal with pulses and noise.
    """
    if data_time_signal_kwargs is None:
        data_time_signal_kwargs = {}

    if not pulses:
        raise ValueError("The list of pulses is empty.")

    # Sort pulses by their start time
    pulses_sorted = sorted(pulses, key=lambda pulse: pulse.time_s[0])

    # Determine the overall time range
    pulse_start_times = [pulse.time_s[0] for pulse in pulses_sorted]
    pulse_end_times = [pulse.time_s[-1] for pulse in pulses_sorted]

    # Set start_time and end_time based on parameters or pulses
    if start_time_s is not None:
        if start_time_s > min(pulse_start_times):
            raise ValueError("start_time_s is after the start time of some pulses.")
        start_time = start_time_s
    else:
        start_time = min(pulse_start_times)

    if end_time_s is not None:
        if end_time_s < max(pulse_end_times):
            raise ValueError("end_time_s is before the end time of some pulses.")
        end_time = end_time_s
    else:
        end_time = max(pulse_end_times)

    # Determine the sampling rate from the first pulse
    first_pulse = pulses_sorted[0]
    if len(first_pulse.time_s) < 2:
        raise ValueError(
            "Each pulse must contain at least two time points to determine sampling rate."
        )

    sampling_intervals = np.diff(first_pulse.time_s)
    mean_sampling_interval = np.mean(sampling_intervals)
    sampling_rate = 1.0 / mean_sampling_interval

    # Create the full time array
    full_time_s = np.arange(
        start_time, end_time + mean_sampling_interval, mean_sampling_interval
    )

    # Initialize the full data array with noise
    if noise_std is None:
        # Estimate noise_std from pulses by assuming pulses are signal and noise is lower
        # Take the minimum standard deviation across all pulses
        noise_std_estimates = [
            np.std(pulse.data) for pulse in pulses_sorted if len(pulse.data) > 1
        ]
        if not noise_std_estimates:
            raise ValueError(
                "Cannot estimate noise standard deviation from the provided pulses."
            )
        noise_std = min(noise_std_estimates)

    # Generate noise for the entire duration using the defined function
    # Create a dummy pulse to initialize the noise generator
    dummy_pulse = pulses[0]
    noise_generator = extract_off_state_generator_from_full_state_data(
        dummy_pulse,
        baseline=baseline,
        sampling_rate=sampling_rate,
    )

    # Generate noise for the entire duration
    noise_segment = noise_generator(end_time - start_time)
    noise_data = np.array(noise_segment.data)

    # **Modified Section Starts Here**
    # Ensure that the generated noise matches the full_time_s length
    if len(noise_data) < len(full_time_s):
        pad_length = len(full_time_s) - len(noise_data)
        additional_time_s = pad_length * mean_sampling_interval

        # Generate additional noise using the noise generator to match the original noise style
        additional_noise_segment = noise_generator(
            additional_time_s, num_samples=pad_length
        )
        additional_noise_data = np.array(additional_noise_segment.data)

        # Handle cases where the noise generator might return more data than needed
        if len(additional_noise_data) < pad_length:
            raise ValueError(
                f"Noise generator could not generate enough data for padding. "
                f"Required: {pad_length}, Generated: {len(additional_noise_data)}"
            )
        # Truncate to the required pad length
        additional_noise_data = additional_noise_data[:pad_length]

        # Concatenate the additional noise to the original noise_data
        noise_data = np.concatenate([noise_data, additional_noise_data])
    elif len(noise_data) > len(full_time_s):
        noise_data = noise_data[: len(full_time_s)]
    # **Modified Section Ends Here**

    full_data = noise_data.copy()

    # Implement verification to ensure pulses do not overlap
    for i in range(1, len(pulses_sorted)):
        previous_pulse_end = pulses_sorted[i - 1].time_s[-1]
        current_pulse_start = pulses_sorted[i].time_s[0]
        if current_pulse_start < previous_pulse_end:
            raise ValueError(f"Pulses at index {i-1} and {i} are overlapping.")

    # Insert each pulse into the full data array at the correct indices
    for pulse in pulses_sorted:
        pulse_time_s = np.array(pulse.time_s)
        pulse_data = np.array(pulse.data)

        # Find the start and end indices of the pulse in the full_time_s array
        pulse_start_time = pulse_time_s[0]
        # pulse_end_time = pulse_time_s[-1]

        # Calculate the corresponding indices
        pulse_start_idx = int(np.round((pulse_start_time - start_time) * sampling_rate))
        pulse_end_idx = pulse_start_idx + len(pulse_data)

        # Handle boundary conditions
        if pulse_start_idx < 0:
            raise ValueError(
                f"Pulse start time {pulse_start_time} is before the full signal start time {start_time}."
            )
        if pulse_end_idx > len(full_data):
            # Trim the pulse data if it exceeds the full signal end time
            pulse_data = pulse_data[: len(full_data) - pulse_start_idx]
            pulse_end_idx = len(full_data)

        # Insert the pulse data
        full_data[pulse_start_idx:pulse_end_idx] = pulse_data

    # Create the composed TimeSignalData instance
    composed_signal = TimeSignalData(
        time_s=full_time_s.tolist(),
        data=full_data.tolist(),
        data_name="ComposedSignal",
        **data_time_signal_kwargs,
    )

    return composed_signal
