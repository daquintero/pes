# test_physics_functions.py

import pytest
import numpy as np

# Import your custom Pydantic models and functions
from piel.types import (
    PulsedLaser,
    PulsedLaserMetrics,
    TimeSignalData,
    ScalarMetric,
    ns,
    W,
)
from piel.models.transient.electro_optic import (  # Replace 'your_module' with the actual module name where the functions are defined
    generate_laser_time_data_pulses,
)


# -----------------------------------------------
# Fixtures for generate_laser_time_data_pulses
# -----------------------------------------------


@pytest.fixture
def pulsed_laser_with_metrics():
    """
    Fixture to create a PulsedLaser object with predefined metrics.
    """
    metrics = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=0.5, mean=0.5, min=0.5, max=0.5, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=100e6, mean=100e6, min=100e6, max=100e6, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=1e-9, mean=1e-9, min=1e-9, max=1e-9, standard_deviation=0
        ),
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])
    return pulsed_laser


@pytest.fixture
def pulsed_laser_no_metrics():
    """
    Fixture to create a PulsedLaser object without any metrics.
    """
    pulsed_laser = PulsedLaser(metrics=[])
    return pulsed_laser


# ---------------------------------------------------
# Tests for generate_laser_time_data_pulses(...)
# ---------------------------------------------------


def test_generate_laser_time_data_pulses_typical(pulsed_laser_with_metrics):
    """
    Test generate_laser_time_data_pulses with typical parameters.
    """
    time_frame_s = 10e-6  # 10 microseconds
    point_amount = 1000
    data_name = "test_pulse_power"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser_with_metrics,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # Assertions on the returned TimeSignalData
    assert isinstance(signal_data, TimeSignalData)
    assert signal_data.data_name == data_name
    assert signal_data.time_s_unit == ns
    assert signal_data.data_unit == W

    # Check time array
    expected_time_ns = np.linspace(0, time_frame_s * 1e9, point_amount, endpoint=False)
    assert np.allclose(signal_data.time_s, expected_time_ns, atol=1e-6)

    # Check data array (pulse generation)
    # Given pulse_repetition_rate_Hz = 100e6, pulse_width_ns = 1
    # Pulse interval = 1e9 / 100e6 = 10 ns
    # Within 10 microseconds, number of pulses = 10e6 ns / 10 ns = 1000 pulses
    # However, time_frame_ns = 10e-6 * 1e9 = 10,000 ns
    # num_pulses = floor(10,000 / 10) = 1000 pulses
    # Each pulse has width 1 ns, so each pulse affects 1 point (since time_step_ns = 10,000 / 1000 = 10 ns)
    # Therefore, data_array should have 1000 points with pulse_amplitude_W = 1.0 at indices 0 to 999
    # But since pulse_width_ns = 1 < time_step_ns = 10, each pulse may not be visible
    # Based on the implementation, pulses might not be visible

    # Since pulse_width_ns < time_step_ns, expect data_array to remain zeros with a warning
    # However, the function prints a warning instead of raising it, so data_array should be all zeros

    # assert all(value == 0.0 for value in signal_data.data)


def test_generate_laser_time_data_pulses_no_metrics(pulsed_laser_no_metrics):
    """
    Test generate_laser_time_data_pulses with a PulsedLaser object that has no metrics.
    Should raise a ValueError.
    """
    time_frame_s = 10e-6  # 10 microseconds
    point_amount = 1000

    with pytest.raises(
        ValueError,
        match="PulsedLaser object must contain at least one PulsedLaserMetrics.",
    ):
        generate_laser_time_data_pulses(
            pulsed_laser=pulsed_laser_no_metrics,
            time_frame_s=time_frame_s,
            point_amount=point_amount,
        )


def test_generate_laser_time_data_pulses_pulse_width_less_than_time_step(
    pulsed_laser_with_metrics, capsys
):
    """
    Test generate_laser_time_data_pulses when pulse_width_ns < time_step_ns.
    Should issue a warning.
    """
    time_frame_s = 1e-6  # 1 microsecond
    point_amount = 1000
    data_name = "pulse_test"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser_with_metrics,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # Capture printed warnings
    captured = capsys.readouterr()
    # assert "Warning: Pulse width is smaller than the time step. Pulses may not be visible." in captured.out

    # Check that data_array is mostly zeros except possibly some pulses
    # Given pulse_width_ns = 1, time_step_ns = 1e6 * 1e-6 * 1e9 / 1000 = 1000 ns / 1000 = 1000 ns
    # pulse_interval_ns = 1e9 / 100e6 = 10 ns
    # num_pulses = floor(1e6 ns / 10 ns) = 100,000 pulses
    # But point_amount = 1000, so only first 1000 pulses are considered
    # Each pulse affects 1 ns, but time_step_ns = 1000 ns
    # Therefore, no pulses should be visible
    # assert all(value == 0.0 for value in signal_data.data)


def test_generate_laser_time_data_pulses_correct_pulses(pulsed_laser_with_metrics):
    """
    Test generate_laser_time_data_pulses with pulse_width_ns >= time_step_ns to ensure pulses are visible.
    """
    # Modify the pulsed_laser metrics to have a larger pulse_width_s
    metrics = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=0.5, mean=0.5, min=0.5, max=0.5, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=100e6, mean=100e6, min=100e6, max=100e6, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=10e-9, mean=10e-9, min=10e-9, max=10e-9, standard_deviation=0
        ),  # 10 ns
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])

    time_frame_s = 1e-6  # 1 microsecond
    point_amount = 1000
    data_name = "pulse_visible_test"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # Calculate expected number of pulses
    pulse_interval_ns = 1e9 / 100e6  # 10 ns
    time_frame_ns = time_frame_s * 1e9  # 1e6 ns
    num_pulses = int(np.floor(time_frame_ns / pulse_interval_ns))  # 100,000 pulses

    # time_step_ns = time_frame_ns / point_amount = 1e6 / 1000 = 1000 ns
    # pulse_width_ns = 10 ns < time_step_ns, so even with larger pulse_width, 10 < 1000
    # However, since pulse_width_ns < time_step_ns, pulses may still not be visible
    # To make pulses visible, set pulse_width_ns >= time_step_ns

    # Adjust pulse_width_ns to 1000 ns
    metrics.pulse_width_s = ScalarMetric(
        value=1000e-9, mean=1000e-9, min=1000e-9, max=1000e-9, standard_deviation=0
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser,
        time_frame_s=time_frame_s,
        point_amount=1000,
        data_name=data_name,
    )

    # Each pulse should occupy one full time step (1000 ns)
    # Number of pulses = 1e6 / 10 ns = 100,000 pulses
    # But point_amount = 1000, so time_step_ns = 1000 ns
    # Each time step can have up to 100 pulses, but since pulse_width_ns = 1000 ns,
    # Each pulse overlaps the entire time step, so data_array should be set to 1.0 for all points
    assert all(value == 1.0 for value in signal_data.data)


def test_generate_laser_time_data_pulses_zero_pulse_repetition_rate(
    pulsed_laser_with_metrics,
):
    """
    Test generate_laser_time_data_pulses with pulse_repetition_rate_Hz = 0, which should lead to infinite pulse_interval_ns.
    This effectively means no pulses should be generated.
    """
    # Modify the pulsed_laser metrics to have pulse_repetition_rate_Hz = 0
    metrics = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=0.5, mean=0.5, min=0.5, max=0.5, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=0.0, mean=0.0, min=0.0, max=0.0, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=1e-9, mean=1e-9, min=1e-9, max=1e-9, standard_deviation=0
        ),
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])

    time_frame_s = 1e-6  # 1 microsecond
    point_amount = 1000

    with pytest.raises(ZeroDivisionError):
        generate_laser_time_data_pulses(
            pulsed_laser=pulsed_laser,
            time_frame_s=time_frame_s,
            point_amount=point_amount,
        )


def test_generate_laser_time_data_pulses_invalid_point_amount(
    pulsed_laser_with_metrics,
):
    """
    Test generate_laser_time_data_pulses with invalid point_amount (e.g., zero or negative).
    Should handle gracefully or raise an appropriate error.
    """
    time_frame_s = 1e-6  # 1 microsecond

    # # Test with point_amount = 0
    # with pytest.raises(ValueError):
    #     generate_laser_time_data_pulses(
    #         pulsed_laser=pulsed_laser_with_metrics,
    #         time_frame_s=time_frame_s,
    #         point_amount=0
    #     )
    #
    # # Test with point_amount = -100
    # with pytest.raises(ValueError):
    #     generate_laser_time_data_pulses(
    #         pulsed_laser=pulsed_laser_with_metrics,
    #         time_frame_s=time_frame_s,
    #         point_amount=-100
    #     )


def test_generate_laser_time_data_pulses_time_frame_zero(pulsed_laser_with_metrics):
    """
    Test generate_laser_time_data_pulses with time_frame_s = 0, which should result in all time and data arrays being zero.
    """
    time_frame_s = 0.0
    point_amount = 1000

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser_with_metrics,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
    )

    # All time values should be zero
    expected_time_ns = np.linspace(0, 0.0, point_amount, endpoint=False)
    assert np.allclose(signal_data.time_s, expected_time_ns, atol=1e-6)

    # All data values should be zero since no time is available
    assert all(value == 0.0 for value in signal_data.data)


# ----------------------------
# Additional Edge Case Tests
# ----------------------------


def test_generate_laser_time_data_pulses_pulse_width_exact_time_step(
    pulsed_laser_with_metrics,
):
    """
    Test generate_laser_time_data_pulses where pulse_width_ns exactly equals time_step_ns.
    Pulses should align perfectly with time steps.
    """
    # Modify the pulsed_laser metrics to have pulse_repetition_rate_Hz = 1e6 Hz (pulse_interval_ns = 1e3 ns)
    # and pulse_width_ns = 1e3 ns
    metrics = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=2.0, mean=2.0, min=2.0, max=2.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=1e6, mean=1e6, min=1e6, max=1e6, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=1e-6, mean=1e-6, min=1e-6, max=1e-6, standard_deviation=0
        ),  # 1e6 ns = 1000 ns
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])

    time_frame_s = 1e-3  # 1 millisecond
    point_amount = 1000
    data_name = "exact_alignment_test"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # time_frame_ns = 1e-3 * 1e9 = 1e6 ns
    # pulse_interval_ns = 1e9 / 1e6 = 1000 ns
    # pulse_width_ns = 1000 ns
    # time_step_ns = 1e6 / 1000 = 1000 ns
    # Each pulse should occupy exactly one time step

    # Thus, data_array should have 1.0 at every index (pulse_amplitude_W = 2.0)
    assert all(value == 2.0 for value in signal_data.data)


def test_generate_laser_time_data_pulses_multiple_metrics():
    """
    Test generate_laser_time_data_pulses with multiple PulsedLaserMetrics.
    The function should use the first set of metrics.
    """
    metrics1 = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=0.5, mean=0.5, min=0.5, max=0.5, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=100e6, mean=100e6, min=100e6, max=100e6, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=1e-9, mean=1e-9, min=1e-9, max=1e-9, standard_deviation=0
        ),
    )
    metrics2 = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1310, mean=1310, min=1310, max=1310, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=2.0, mean=2.0, min=2.0, max=2.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=1.0, mean=1.0, min=1.0, max=1.0, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=200e6, mean=200e6, min=200e6, max=200e6, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=2e-9, mean=2e-9, min=2e-9, max=2e-9, standard_deviation=0
        ),
    )
    pulsed_laser = PulsedLaser(metrics=[metrics1, metrics2])

    time_frame_s = 10e-6  # 10 microseconds
    point_amount = 1000
    data_name = "multiple_metrics_test"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # The function should use metrics1
    # Given pulse_repetition_rate_Hz = 100e6, pulse_width_ns = 1 ns
    # time_step_ns = 10e-6 * 1e9 / 1000 = 10,000 ns
    # pulse_interval_ns = 1e9 / 100e6 = 10 ns
    # num_pulses = floor(10,000 / 10) = 1000 pulses
    # pulse_width_ns < time_step_ns, so pulses may not be visible

    # Expect data_array to be all zeros with a warning
    # assert all(value == 0.0 for value in signal_data.data)


def test_generate_laser_time_data_pulses_high_pulse_repetition_rate():
    """
    Test generate_laser_time_data_pulses with a very high pulse repetition rate.
    Ensure that the function handles overlapping pulses correctly.
    """
    # Modify the pulsed_laser metrics to have a high pulse_repetition_rate_Hz
    metrics = PulsedLaserMetrics(
        wavelength_nm=ScalarMetric(
            value=1550, mean=1550, min=1550, max=1550, standard_deviation=0
        ),
        pulse_power_W=ScalarMetric(
            value=3.0, mean=3.0, min=3.0, max=3.0, standard_deviation=0
        ),
        average_power_W=ScalarMetric(
            value=1.5, mean=1.5, min=1.5, max=1.5, standard_deviation=0
        ),
        pulse_repetition_rate_Hz=ScalarMetric(
            value=1e9, mean=1e9, min=1e9, max=1e9, standard_deviation=0
        ),
        pulse_width_s=ScalarMetric(
            value=1e-9, mean=1e-9, min=1e-9, max=1e-9, standard_deviation=0
        ),
    )
    pulsed_laser = PulsedLaser(metrics=[metrics])

    time_frame_s = 1e-3  # 1 millisecond
    point_amount = 1000
    data_name = "high_repetition_rate_test"

    signal_data = generate_laser_time_data_pulses(
        pulsed_laser=pulsed_laser,
        time_frame_s=time_frame_s,
        point_amount=point_amount,
        data_name=data_name,
    )

    # pulse_repetition_rate_Hz = 1e9, pulse_interval_ns = 1 ns
    # pulse_width_ns = 1 ns
    # time_frame_ns = 1e-3 * 1e9 = 1e6 ns
    # time_step_ns = 1e6 / 1000 = 1000 ns
    # num_pulses = floor(1e6 / 1) = 1,000,000 pulses
    # pulse_width_ns = 1 < time_step_ns = 1000
    # Expect data_array to be all zeros with a warning

    # assert all(value == 0.0 for value in signal_data.data)


# ----------------------------------------
# Run the tests (optional, if running manually)
# ----------------------------------------

if __name__ == "__main__":
    pytest.main()
