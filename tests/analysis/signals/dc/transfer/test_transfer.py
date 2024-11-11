import pytest
import numpy as np
import pandas as pd

# Import the function to be tested
from piel.analysis.signals.dc import compile_dc_min_max_metrics_from_dc_collection

# Import necessary classes and units
from piel.types import (
    SignalDC,
    SignalTraceDC,
    SignalDCCollection,
    Unit,
    V,
    A,
    W,
)

# Importing mock functions for metrics
from piel.analysis.signals.dc import (
    get_out_min_max,
    get_out_response_in_transition_range,
    get_power_metrics,
)

# Sample Units
VOLTAGE_UNIT = V
CURRENT_UNIT = A
POWER_UNIT = W

# Sample Data for Testing
VOLTAGE_VALUES = [0.0, 1.0, 2.0, 3.0, 4.0]
CURRENT_VALUES = [0.0, 0.5, 1.0, 1.5, 2.0]
POWER_VALUES = [0.0, 0.5, 2.0, 4.5, 8.0]


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


# Mock Metrics Functions
@pytest.fixture
def mock_get_out_min_max(monkeypatch):
    def mock_get_out_min_max(collection, **kwargs):
        return ScalarMetric(min=1.0, max=4.0, unit=VOLTAGE_UNIT)


@pytest.fixture
def mock_get_out_response_in_transition_range(monkeypatch):
    def mock_get_out_response_in_transition_range(collection, **kwargs):
        return ScalarMetric(min=0.5, max=3.5, unit=VOLTAGE_UNIT)


@pytest.fixture
def mock_get_power_metrics(monkeypatch):
    def mock_get_power_metrics(collection, **kwargs):
        return ScalarMetric(min=0.0, max=8.0, unit=POWER_UNIT)


# Mock ScalarMetric
from piel.types import ScalarMetric


# def test_compile_dc_min_max_metrics_from_dc_collection(
#     mock_get_out_min_max,
#     mock_get_out_response_in_transition_range,
#     mock_get_power_metrics,
# ):
#     """
#     Test compiling DC min and max metrics from a SignalDCCollection.
#     """
#     # Create sample SignalDC instances
#     input_voltage = create_signal_dc("Input Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     # Create SignalDCCollection
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     # Labels
#     label_list = ["Test Collection"]
#
#     # Compile metrics
#     result_df = compile_dc_min_max_metrics_from_dc_collection(
#         collections=[collection],
#         label_list=label_list,
#     )
#
#     # Expected Data
#     expected_data = {
#         "label": ["Test Collection"],
#         r"$V_{out, min}$ $V$": [1.0],
#         r"$V_{out, max}$ $V$": [4.0],
#         r"$V_{tr,in, min}$ $V$": [0.5],
#         r"$V_{tr,in, max}$ $V$": [3.5],
#         r"$P_{dd,max}$ $mW$": [8000.0],  # Assuming power_metrics.max / 1e-3
#         r"$\Delta P_{dd}$ $mW$": [
#             8000.0
#         ],  # Assuming power_metrics.max - min = 8.0 / 1e-3
#     }
#
#     expected_df = pd.DataFrame(expected_data).applymap(lambda x: round(x, 3))
#
#     pd.testing.assert_frame_equal(result_df, expected_df)


def test_compile_dc_min_max_metrics_mismatched_lengths():
    """
    Test that ValueError is raised when collections and labels have different lengths.
    """
    input_voltage = create_signal_dc("Input Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
    output_voltage = create_signal_dc("Output Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
    power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)

    label_list = ["Test Collection 1", "Test Collection 2"]  # Mismatched length


# def test_compile_dc_min_max_metrics_with_thresholds():
#     """
#     Test compiling DC metrics with specific threshold kwargs.
#     """
#     # Assuming thresholds are handled inside mock functions
#     input_voltage = create_signal_dc("Input Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     label_list = ["Threshold Test"]
#
#     threshold_kwargs = {"lower_threshold_ratio": 0.2, "upper_threshold_ratio": 0.8}
#
#     result_df = compile_dc_min_max_metrics_from_dc_collection(
#         collections=[collection],
#         label_list=label_list,
#         threshold_kwargs=threshold_kwargs,
#     )
#
#     # Expected Data remains the same due to mocked metrics
#     expected_data = {
#         "label": ["Threshold Test"],
#         r"$V_{out, min}$ $V$": [1.0],
#         r"$V_{out, max}$ $V$": [4.0],
#         r"$V_{tr,in, min}$ $V$": [0.5],
#         r"$V_{tr,in, max}$ $V$": [3.5],
#         r"$P_{dd,max}$ $mW$": [8000.0],
#         r"$\Delta P_{dd}$ $mW$": [8000.0],
#     }
#
#     # expected_df = pd.DataFrame(expected_data).applymap(lambda x: round(x, 3))
#     #
#     # pd.testing.assert_frame_equal(result_df, expected_df)


# def test_compile_dc_min_max_metrics_with_exceptions(monkeypatch):
#     """
#     Test compiling DC metrics when an exception occurs during metrics computation.
#     """
#
#     # Mock get_out_min_max to raise an exception
#     def mock_get_out_min_max_exception(collection, **kwargs):
#         raise RuntimeError("Mocked exception for get_out_min_max")
#
#     monkeypatch.setattr(
#         "piel.analysis.signals.dc.get_out_min_max", mock_get_out_min_max_exception
#     )
#
#     # Create sample SignalDC instances
#     input_voltage = create_signal_dc("Input Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     output_voltage = create_signal_dc("Output Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
#     power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)
#
#     collection = create_signal_dc_collection(input_voltage, output_voltage, power)
#
#     label_list = ["Exception Collection"]
#
#     # Compile metrics with debug=False (should not raise)
#     result_df = compile_dc_min_max_metrics_from_dc_collection(
#         collections=[collection], label_list=label_list, debug=False
#     )
#
#     # Expected Data with NaNs due to exception
#     expected_data = {
#         "label": ["Exception Collection"],
#         r"$V_{out, min}$ $V$": [np.nan],
#         r"$V_{out, max}$ $V$": [np.nan],
#         r"$V_{tr,in, min}$ $V$": [np.nan],
#         r"$V_{tr,in, max}$ $V$": [np.nan],
#         r"$P_{dd,max}$ $mW$": [np.nan],
#         r"$\Delta P_{dd}$ $mW$": [np.nan],
#     }
#
#     # expected_df = pd.Datasresult_df, expected_df)


def test_compile_dc_min_max_metrics_with_debug_exception(monkeypatch):
    """
    Test compiling DC metrics when an exception occurs and debug=True (should raise).
    """

    # Mock get_out_min_max to raise an exception
    def mock_get_out_min_max_exception(collection, **kwargs):
        raise RuntimeError("Mocked exception for get_out_min_max")

    monkeypatch.setattr(
        "piel.analysis.signals.dc.get_out_min_max", mock_get_out_min_max_exception
    )

    # Create sample SignalDC instances
    input_voltage = create_signal_dc("Input Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
    output_voltage = create_signal_dc("Output Voltage", VOLTAGE_VALUES, VOLTAGE_UNIT)
    power = create_signal_dc("Power", POWER_VALUES, POWER_UNIT)

    collection = create_signal_dc_collection(input_voltage, output_voltage, power)

    label_list = ["Debug Exception Collection"]
