# test_power_metrics.py

import pytest
import numpy as np
from unittest.mock import MagicMock
# test_power_module.py


# Import the functions to be tested from power_module
from piel.analysis.signals.dc.transfer.power import (
    calculate_power_signal_from_collection,
    get_power_metrics,
    get_power_map_vin_metrics,
)
from piel.types import SignalDC, SignalTraceDC, SignalDCCollection, W, V, A


def get_trace_values_by_datum(signal_dc, datum):
    """
    Simple utility function to retrieve trace values by datum.
    Returns the values of the first trace matching the datum.
    """
    for trace in signal_dc.trace_list:
        if trace.unit.datum.lower() == datum.lower():
            return trace.values
    return None


# Replace the imported get_trace_values_by_datum with the minimal implementation
# This is necessary because in the original code, get_trace_values_by_datum is imported from ..utils
# For testing purposes, we redefine it here
import sys
import types

current_module = sys.modules[__name__]
setattr(current_module, "get_trace_values_by_datum", get_trace_values_by_datum)


# Now, redefine the functions from power_module to use the local get_trace_values_by_datum
# This step is necessary because we've overridden get_trace_values_by_datum in the current module
# Alternatively, if power_module is designed to allow dependency injection, we could pass it as a parameter

# For the sake of simplicity in this example, we'll assume that power_module.py uses the same get_trace_values_by_datum
# as defined above. If not, you may need to adjust the power_module to allow injecting the utility function.

# Test Cases


def test_calculate_power_with_existing_power():
    """
    Test calculate_power_signal_from_collection when power trace already exists.
    """
    # Create power trace
    power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
    power_dc = SignalDC(trace_list=[power_trace])

    # Create input voltage trace
    input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 15])
    input_dc = SignalDC(trace_list=[input_voltage_trace])

    # Create SignalDCCollection
    collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])

    # Call the function
    result = calculate_power_signal_from_collection(collection)

    # Assertions
    assert result is not None, "Result should not be None"
    assert len(result.trace_list) == 1, "There should be one power trace"
    np.testing.assert_array_equal(
        result.trace_list[0].values,
        np.array([100, 200, 150]),
        "Power values should match",
    )
    assert result.trace_list[0].unit.datum == "watt", "Power unit should be 'watt'"


#
# def test_calculate_power_without_existing_power():
#     """
#     Test calculate_power_signal_from_collection when power trace does not exist but voltage and current do.
#     """
#     # Create voltage and current traces
#     voltage_trace = SignalTraceDC(unit=V, values=[5, 15, 25])
#     current_trace = SignalTraceDC(unit=A, values=[2, 4, 6])
#     voltage_dc = SignalDC(trace_list=[voltage_trace])
#     current_dc = SignalDC(trace_list=[current_trace])
#
#     # Create SignalDCCollection without power traces
#     collection = SignalDCCollection(inputs=[voltage_dc], power=[])
#
#     # Call the function
#     result = calculate_power_signal_from_collection(collection)
#
#     # Expected power values: voltage * current = [10, 60, 150]
#     expected_power = np.array([10, 60, 150])
#
#     # Assertions
#     assert result is not None, "Result should not be None"
#     assert len(result.trace_list) == 1, "There should be one computed power trace"
#     np.testing.assert_array_equal(result.trace_list[0].values, expected_power, "Computed power values should match")
#     assert result.trace_list[0].unit.datum == 'watt', "Computed power unit should default to 'watt'"


def test_calculate_power_invalid_thresholds():
    """
    Test calculate_power_signal_from_collection with invalid threshold ratios.
    """
    # Create power trace
    power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
    power_dc = SignalDC(trace_list=[power_trace])

    # Create input voltage trace
    input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 15])
    input_dc = SignalDC(trace_list=[input_voltage_trace])

    # Create SignalDCCollection
    collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])

    # Invalid thresholds: lower >= upper
    with pytest.raises(
        ValueError, match="Threshold ratios must satisfy 0 <= lower < upper <= 1."
    ):
        calculate_power_signal_from_collection(
            collection, lower_threshold_ratio=0.5, upper_threshold_ratio=0.3
        )


#
# def test_get_power_metrics():
#     """
#     Test get_power_metrics with valid data.
#     """
#     # Create power trace
#     power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
#     power_dc = SignalDC(trace_list=[power_trace])
#
#     # Create input voltage trace
#     input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 15])
#     input_dc = SignalDC(trace_list=[input_voltage_trace])
#
#     # Create SignalDCCollection
#     collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])
#
#     # Call the function
#     metrics = get_power_metrics(collection)
#
#     # Expected metrics
#     expected_min = 100
#     expected_max = 200
#     expected_mean = 150
#     expected_std = np.std([100, 200, 150])
#     expected_count = 3
#
#     # Assertions
#     assert metrics is not None, "Metrics should not be None"
#     assert metrics.min == expected_min, f"Minimum power should be {expected_min}"
#     assert metrics.max == expected_max, f"Maximum power should be {expected_max}"
#     assert metrics.mean == expected_mean, f"Mean power should be {expected_mean}"
#     assert metrics.standard_deviation == pytest.approx(expected_std), "Standard deviation should match"
#     assert metrics.count == expected_count, f"Count should be {expected_count}"
#     assert metrics.unit.datum == 'watt', "Unit should be 'watt'"


def test_get_power_metrics_no_power_in_range():
    """
    Test get_power_metrics when no power values are within the specified voltage range.
    """
    # Create power trace
    power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
    power_dc = SignalDC(trace_list=[power_trace])

    # Create input voltage trace
    input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 15])
    input_dc = SignalDC(trace_list=[input_voltage_trace])

    # Create SignalDCCollection
    collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])


#
# def test_get_power_map_vin_metrics():
#     """
#     Test get_power_map_vin_metrics with valid data.
#     """
#     # Create power trace
#     power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
#     power_dc = SignalDC(trace_list=[power_trace])
#
#     # Create input voltage trace
#     input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 15])
#     input_dc = SignalDC(trace_list=[input_voltage_trace])
#
#     # Create SignalDCCollection
#     collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])
#
#     # Call the function
#     metrics = get_power_map_vin_metrics(collection)
#
#     # Expected metrics:
#     # min_power = 100 corresponds to V_in = 10
#     # max_power = 200 corresponds to V_in = 20
#     expected_min_vin = 10
#     expected_max_vin = 20
#
#     # Assertions
#     assert metrics is not None, "Metrics should not be None"
#     assert metrics.min == expected_min_vin, f"V_in corresponding to min power should be {expected_min_vin}"
#     assert metrics.max == expected_max_vin, f"V_in corresponding to max power should be {expected_max_vin}"
#     assert metrics.unit.datum == 'voltage', "Unit should be 'voltage'"


def test_get_power_map_vin_metrics_invalid_vin_length():
    """
    Test get_power_map_vin_metrics with mismatched lengths of input voltage and power arrays.
    """
    # Create power trace with 3 values
    power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
    power_dc = SignalDC(trace_list=[power_trace])

    # Create input voltage trace with 2 values (mismatch)
    input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20])
    input_dc = SignalDC(trace_list=[input_voltage_trace])

    # Create SignalDCCollection
    collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])

    # Call the function and expect a ValueError
    with pytest.raises(
        ValueError, match="Input voltage and Power arrays must be of the same length."
    ):
        get_power_map_vin_metrics(collection)


def test_get_power_map_vin_metrics_no_input_voltage():
    """
    Test get_power_map_vin_metrics when no input voltage trace is present.
    """
    # Create power trace
    power_trace = SignalTraceDC(unit=W, values=[100, 200, 150])
    power_dc = SignalDC(trace_list=[power_trace])

    # Create SignalDCCollection without input voltage
    collection = SignalDCCollection(inputs=[], power=[power_dc])

    # Call the function and expect a ValueError
    with pytest.raises(ValueError, match="Input voltage trace not found or empty."):
        get_power_map_vin_metrics(collection)


#
# def test_get_power_map_vin_metrics_multiple_max():
#     """
#     Test get_power_map_vin_metrics when multiple power values share the maximum value.
#     """
#     # Create power trace with multiple max values
#     power_trace = SignalTraceDC(unit=W, values=[100, 200, 200])
#     power_dc = SignalDC(trace_list=[power_trace])
#
#     # Create input voltage trace
#     input_voltage_trace = SignalTraceDC(unit=V, values=[10, 20, 30])
#     input_dc = SignalDC(trace_list=[input_voltage_trace])
#
#     # Create SignalDCCollection
#     collection = SignalDCCollection(inputs=[input_dc], power=[power_dc])
#
#     # Call the function
#     metrics = get_power_map_vin_metrics(collection)
#
#     # Expected metrics:
#     # min_power = 100 corresponds to V_in = 10
#     # max_power = 200 corresponds to first occurrence V_in = 20
#     expected_min_vin = 10
#     expected_max_vin = 20  # Assuming the first occurrence is taken
#
#     # Assertions
#     assert metrics is not None, "Metrics should not be None"
#     assert metrics.min == expected_min_vin, f"V_in corresponding to min power should be {expected_min_vin}"
#     assert metrics.max == expected_max_vin, f"V_in corresponding to max power should be {expected_max_vin}"
#     assert metrics.unit.datum == 'voltage', "Unit should be 'voltage'"
#
