import numpy as np
from piel.types import PulsedLaser, TimeSignalData, ns, W


def generate_laser_time_data_pulses(
    pulsed_laser: PulsedLaser,
    time_frame_s: float,
    point_amount: int,
    data_name: str = "optical_pulse_power",
) -> TimeSignalData:
    """
    Converts PulsedLaser metrics into a time-domain signal representation.

    Parameters:
    - pulsed_laser (PulsedLaser): The pulsed laser object containing metrics.
    - time_frame_s (float): Total duration of the time signal in seconds.
    - point_amount (int): Number of points in the time and data arrays.
    - data_name (str): Name/description of the data signal.

    Returns:
    - TimeSignalData: The time-domain signal data.
    """
    if not pulsed_laser.metrics:
        raise ValueError(
            "PulsedLaser object must contain at least one PulsedLaserMetrics."
        )

    # Assuming we use the first set of metrics
    metrics = pulsed_laser.metrics[0]

    time_frame_ns = time_frame_s * 1e9

    # Extract necessary metrics with proper unit conversions
    pulse_repetition_rate_Hz = metrics.pulse_repetition_rate_Hz.value  # in Hz
    pulse_width_ns = metrics.pulse_width_s.min * 1e9  # Convert seconds to nanoseconds
    pulse_amplitude_W = metrics.pulse_power_W.max  # in Watts

    # Calculate pulse interval in nanoseconds
    pulse_interval_ns = 1e9 / pulse_repetition_rate_Hz  # nanoseconds

    # Calculate the number of pulses that fit within the time frame
    num_pulses = int(np.floor(time_frame_ns / pulse_interval_ns))

    # Generate pulse start and end times in nanoseconds
    pulse_start_times_ns = np.arange(num_pulses) * pulse_interval_ns
    pulse_end_times_ns = pulse_start_times_ns + pulse_width_ns

    # Ensure that pulse_end_times_ns do not exceed the total time frame
    pulse_end_times_ns = np.clip(pulse_end_times_ns, None, time_frame_ns)

    # Calculate time step in nanoseconds
    time_step_ns = time_frame_ns / point_amount

    # Check if pulse_width_ns is at least one time step
    if pulse_width_ns < time_step_ns:
        print(
            "Warning: Pulse width is smaller than the time step. Pulses may not be visible."
        )

    # Generate the time array in nanoseconds
    time_array_ns = np.linspace(0, time_frame_ns, point_amount, endpoint=False)

    # Initialize data array with zeros
    data_array = np.zeros(point_amount)

    # Find start and end indices for each pulse using searchsorted
    start_indices = np.searchsorted(time_array_ns, pulse_start_times_ns, side="left")
    end_indices = np.searchsorted(time_array_ns, pulse_end_times_ns, side="right")

    # Ensure that end_indices are within bounds
    end_indices = np.clip(end_indices, 0, point_amount)

    # Assign pulse amplitudes using vectorized operations
    for start, end in zip(start_indices, end_indices):
        if start < end:
            data_array[start:end] = pulse_amplitude_W

    # Create TimeSignalData object
    signal_data = TimeSignalData(
        time_s=time_array_ns.tolist(),  # Time in nanoseconds
        data=data_array.tolist(),
        data_name=data_name,
        time_s_unit=ns,  # nanoseconds
        data_unit=W,  # Watts
    )

    return signal_data
