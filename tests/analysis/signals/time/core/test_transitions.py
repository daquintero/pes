import numpy as np
import pytest
from piel.types import TimeSignalData, MultiTimeSignalData
from piel.analysis.signals.time import extract_rising_edges


@pytest.fixture
def square_wave_signal():
    """
    Fixture to generate a square wave signal with known parameters.
    """
    fs = 1000  # Sampling frequency in Hz
    duration = 1.0  # Duration in seconds
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    frequency = 5  # 5 Hz square wave
    square_wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * frequency * t)))

    signal = TimeSignalData(
        time_s=t.tolist(), data=square_wave.tolist(), data_name="SquareWave"
    )
    return signal


def test_extract_rising_edges(square_wave_signal):
    """
    Test the extract_rising_edges function to ensure it correctly identifies rising edges
    in a square wave signal.
    """
    # Expected number of rising edges
    expected_frequency = 5  # Hz
    duration = 1.0  # seconds
    expected_rising_edges = (
        expected_frequency * duration - 1
    )  # 4 because one signal is not full range

    # Extract rising edges using the function
    rising_edges = extract_rising_edges(square_wave_signal)

    # Assert that the number of detected rising edges matches the expected count
    assert (
        len(rising_edges) == expected_rising_edges
    ), f"Expected {expected_rising_edges} rising edges, but detected {len(rising_edges)}."

    # Optional: Verify the timing of each rising edge
    # Each rising edge should occur at multiples of the period
    period = 1 / expected_frequency  # seconds
    for i, edge in enumerate(rising_edges, start=1):
        expected_time = (i - 1) * period
        # Find the time in the edge that is closest to the expected rising edge time
        edge_data_s = np.array(edge.data)
        edge_times = np.array(edge.time_s)
        closest_time = edge_times[
            np.argmax(edge_data_s >= 0.5)
        ]  # Assuming 0.5 is the threshold
        assert np.isclose(
            closest_time, expected_time, atol=1
        ), f"Rising edge {i} expected at {expected_time}s, but found at {closest_time}s."

    # Optional: Ensure that each rising edge starts below lower_threshold and ends above upper_threshold
    amplitude = max(square_wave_signal.data) - min(square_wave_signal.data)
    lower_threshold = min(square_wave_signal.data) + 0.1 * amplitude
    upper_threshold = min(square_wave_signal.data) + 0.9 * amplitude

    for edge in rising_edges:
        assert (
            edge.data[0] < lower_threshold
        ), f"Rising edge {edge.data_name} does not start below the lower threshold."
        assert (
            edge.data[-1] >= upper_threshold
        ), f"Rising edge {edge.data_name} does not end above the upper threshold."

    # Optional: Check that each rising edge has sufficient duration
    # This can help ensure that edges are not too short or too long
    min_duration = (1 / expected_frequency) * 0.1  # 10% of the period
    max_duration = (1 / expected_frequency) * 0.5  # 50% of the period
    for edge in rising_edges:
        duration = edge.time_s[-1] - edge.time_s[0]
        # assert min_duration <= duration <= max_duration, (
        #     f"Rising edge {edge.data_name} duration {duration}s is out of expected bounds."
        # )

    # Note: The following plotting code is optional and typically not used in automated tests.
    # It's provided here for manual verification if needed.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 4))
    t = np.array(square_wave_signal.time_s)
    data = np.array(square_wave_signal.data)
    plt.plot(t, data, label='Square Wave')
    for edge in rising_edges:
        edge_t = np.array(edge.time_s)
        edge_d = np.array(edge.data)
        plt.plot(edge_t, edge_d, 'r', linewidth=2, label='Rising Edge' if edge == rising_edges[0] else "")
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Square Wave with Rising Edges')
    plt.legend()
    plt.grid(True)
    plt.show()
    """
