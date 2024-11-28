import pytest
import numpy as np

# Import the functions to be tested
from piel.analysis.signals.dc import (
    get_out_min_max,
    get_out_response_in_transition_range,
    calculate_power_signal_from_collection,
    get_power_metrics,
    get_power_map_vin_metrics,
)

# Import necessary classes and units
from piel.types import (
    SignalDC,
    SignalTraceDC,
    SignalDCCollection,
    Unit,
    V,
    A,
    W,
    ScalarMetric,
)

# Sample Units
VOLTAGE_UNIT = V
CURRENT_UNIT = A
POWER_UNIT = W

# Sample Data for Testing
INPUT_VOLTAGE_VALUES = [0.0, 1.0, 2.0, 3.0, 4.0]
OUTPUT_VOLTAGE_VALUES = [0.0, 1.5, 3.0, 4.5, 6.0]
CURRENT_VALUES = [0.0, 0.5, 1.0, 1.5, 2.0]
POWER_VALUES = [0.0, 0.75, 3.0, 6.75, 12.0]


def create_signal_dc(name: str, values: list, unit: Unit) -> SignalDC:
    """
    Helper function to create a SignalDC instance with a single trace.
    """
    trace = SignalTraceDC(name=name, values=values, unit=unit)
    return SignalDC(trace_list=[trace])


def create_signal_dc_collection(
    input_voltage: SignalDC, output_voltage: SignalDC, power: SignalDC
) -> SignalDCCollection:
    """
    Helper function to create a SignalDCCollection instance.
    """
    return SignalDCCollection(
        inputs=[input_voltage], outputs=[output_voltage], power=[power]
    )


#
# def test_get_out_min_max_valid():
#     """
#     Test get_out_min_max with valid data.
#     """
#     # Create SignalDCCollection
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Call get_out_min_max
#     metrics = get_out_min_max(collection, lower_threshold_ratio=0.1, upper_threshold_ratio=0.9)
#
#     assert isinstance(metrics, ScalarMetric), "Should return a ScalarMetric instance."
#     assert metrics.min == 1.0, f"Expected min=1.0, got {metrics.min}"
#     assert metrics.max == 6.0, f"Expected max=6.0, got {metrics.max}"
#     assert metrics.unit == VOLTAGE_UNIT, "Unit should be voltage."


def test_get_out_min_max_invalid_thresholds():
    """
    Test get_out_min_max with invalid threshold ratios.
    """
    input_voltage = create_signal_dc(
        "Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    output_voltage = create_signal_dc(
        "Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)


def test_get_out_min_max_no_traces():
    """
    Test get_out_min_max when no input or output voltage traces are present.
    """
    # Create empty SignalDCCollection
    empty_collection = SignalDCCollection(inputs=[], outputs=[], power=[])

    with pytest.raises(ValueError, match="Input voltage trace not found or empty."):
        get_out_min_max(empty_collection)

    # Add input but no output
    input_voltage = create_signal_dc(
        "Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    collection_no_output = SignalDCCollection(
        inputs=[input_voltage], outputs=[], power=[]
    )


# def test_get_out_response_in_transition_range_valid():
#     """
#     Test get_out_response_in_transition_range with valid data.
#     """
#     # Create SignalDCCollection
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Call get_out_response_in_transition_range
#     metrics = get_out_response_in_transition_range(collection, lower_threshold_ratio=0.2, upper_threshold_ratio=0.8)
#
#     assert isinstance(metrics, ScalarMetric), "Should return a ScalarMetric instance."
#     assert metrics.min == 1.0, f"Expected min=1.0, got {metrics.min}"
#     assert metrics.max == 5.0, f"Expected max=5.0, got {metrics.max}"
#     assert metrics.unit == VOLTAGE_UNIT, "Unit should be voltage."


# def test_calculate_power_signal_from_collection_valid():
#     """
#     Test calculate_power_signal_from_collection with valid data.
#     """
#     # Create SignalDCCollection with explicit power trace
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Call calculate_power_signal_from_collection
#     power_signal_dc = calculate_power_signal_from_collection(collection, lower_threshold_ratio=0.0,
#                                                              upper_threshold_ratio=1.0)
#
#     assert isinstance(power_signal_dc, SignalDC), "Should return a SignalDC instance."
#     assert len(power_signal_dc.trace_list) == 1, "Should contain one power trace."
#     assert power_signal_dc.trace_list[0].unit == POWER_UNIT, "Power unit should be watt."
#     np.testing.assert_array_equal(power_signal_dc.trace_list[0].values, np.array(POWER_VALUES))
#

# def test_calculate_power_signal_from_collection_compute_power():
#     """
#     Test calculate_power_signal_from_collection by computing power from voltage and current.
#     """
#     # Create SignalDCCollection without explicit power trace
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     current = create_signal_dc("Current", CURRENT_VALUES, CURRENT_UNIT)
#
#     # Create collection with power computed from voltage and current
#     collection = SignalDCCollection(inputs=[input_voltage], outputs=[output_voltage], power=[])
#     collection.power = [create_signal_dc("Current", CURRENT_VALUES,
#                                          CURRENT_UNIT)]  # Assuming power is computed from current and voltage
#
#     # Call calculate_power_signal_from_collection
#     power_signal_dc = calculate_power_signal_from_collection(collection, lower_threshold_ratio=0.0,
#                                                              upper_threshold_ratio=1.0)
#
#     assert isinstance(power_signal_dc, SignalDC), "Should return a SignalDC instance."
#     assert len(power_signal_dc.trace_list) == 1, "Should contain one computed power trace."
#     assert power_signal_dc.trace_list[0].unit == W, "Computed power unit should be watt."
#     expected_power = np.array(INPUT_VOLTAGE_VALUES) * np.array(CURRENT_VALUES)
#     np.testing.assert_array_equal(power_signal_dc.trace_list[0].values, expected_power)


def test_calculate_power_signal_from_collection_no_power():
    """
    Test calculate_power_signal_from_collection when no power trace and unable to compute.
    """
    # Create SignalDCCollection without power and without current to compute
    input_voltage = create_signal_dc(
        "Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    output_voltage = create_signal_dc(
        "Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )

    collection = SignalDCCollection(
        inputs=[input_voltage], outputs=[output_voltage], power=[]
    )


# def test_get_power_metrics_valid():
#     """
#     Test get_power_metrics with valid data.
#     """
#     # Create SignalDCCollection
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Call get_power_metrics
#     metrics = get_power_metrics(collection, lower_threshold_ratio=0.0, upper_threshold_ratio=1.0)
#
#     assert isinstance(metrics, ScalarMetric), "Should return a ScalarMetric instance."
#     assert metrics.min == 0.0, f"Expected min=0.0, got {metrics.min}"
#     assert metrics.max == 12.0, f"Expected max=12.0, got {metrics.max}"
#     assert metrics.mean == 3.75, f"Expected mean=3.75, got {metrics.mean}"
#     assert metrics.standard_deviation == 4.743, f"Expected std≈4.743, got {metrics.standard_deviation}"
#     assert metrics.count == 5, f"Expected count=5, got {metrics.count}"
#     assert metrics.unit == W, "Unit should be watt."

#
# def test_get_power_map_vin_metrics_valid():
#     """
#     Test get_power_map_vin_metrics with valid data.
#     """
#     # Create SignalDCCollection
#     input_voltage = create_signal_dc("Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Call get_power_map_vin_metrics
#     metrics = get_power_map_vin_metrics(collection, lower_threshold_ratio=0.0, upper_threshold_ratio=1.0)
#
#     assert isinstance(metrics, ScalarMetric), "Should return a ScalarMetric instance."
#     assert metrics.min == 0.0, f"Expected min V_in=0.0, got {metrics.min}"
#     assert metrics.max == 4.0, f"Expected max V_in=4.0, got {metrics.max}"
#     assert metrics.unit == V, "Unit should be voltage."


def test_get_power_metrics_invalid_thresholds():
    """
    Test get_power_metrics with invalid threshold ratios.
    """
    input_voltage = create_signal_dc(
        "Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    output_voltage = create_signal_dc(
        "Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)


def test_get_power_metrics_no_traces():
    """
    Test get_power_metrics when no input or power traces are present.
    """
    # Create empty SignalDCCollection
    empty_collection = SignalDCCollection(inputs=[], outputs=[], power=[])

    # Add input but no power
    input_voltage = create_signal_dc(
        "Input Voltage", INPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    collection_no_power = SignalDCCollection(
        inputs=[input_voltage], outputs=[], power=[]
    )


def test_get_power_metrics_length_mismatch():
    """
    Test get_power_metrics when input voltage and power arrays have different lengths.
    """
    # Create SignalDCCollection with mismatched lengths
    input_voltage = create_signal_dc("Input Voltage", [0.0, 1.0, 2.0], VOLTAGE_UNIT)
    output_voltage = create_signal_dc(
        "Output Voltage", OUTPUT_VOLTAGE_VALUES, VOLTAGE_UNIT
    )
    power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)  # Length 5

    collection = SignalDCCollection(
        inputs=[input_voltage], outputs=[output_voltage], power=[power]
    )


def test_get_out_min_max_no_data_in_threshold_range():
    """
    Test get_out_min_max when no output voltages are within the threshold range.
    """
    # Create SignalDCCollection with all output voltages outside threshold
    input_voltage = create_signal_dc("Input Voltage", [10.0, 20.0, 30.0], VOLTAGE_UNIT)
    output_voltage = create_signal_dc(
        "Output Voltage", [100.0, 200.0, 300.0], VOLTAGE_UNIT
    )
    power = create_signal_dc("Power", [1000.0, 2000.0, 3000.0], POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)


def test_get_out_response_in_transition_range_no_data():
    """
    Test get_out_response_in_transition_range when no input voltages are within the threshold range.
    """
    # Create SignalDCCollection with all input voltages outside threshold
    input_voltage = create_signal_dc(
        "Input Voltage", [100.0, 200.0, 300.0], VOLTAGE_UNIT
    )
    output_voltage = create_signal_dc(
        "Output Voltage", [10.0, 20.0, 30.0], VOLTAGE_UNIT
    )
    power = create_signal_dc("Power", [1000.0, 2000.0, 3000.0], POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)
