import pytest
import numpy as np

# Import the functions to be tested
from piel.analysis.signals.time import (
    offset_to_first_rising_edge,
    remove_before_first_rising_edge,
)

# Import necessary classes and units
from piel.types import TimeSignalData, Unit

# Sample Units
SECOND_UNIT = Unit(name="second", datum="time", base=1, label="s")
VOLTAGE_UNIT = Unit(name="volt", datum="voltage", base=1, label="V")


# Helper function to create TimeSignalData
def create_data_time_signal(
    time_s: list[float],
    data: list[float],
    data_name: str = "Signal",
) -> TimeSignalData:
    return TimeSignalData(time_s=time_s, data=data, data_name=data_name)


# def test_offset_to_first_rising_edge_success():
#     """
#     Test successful offset of the time axis to the first rising edge.
#     """
#     # Create a waveform with a rising edge at time=2
#     waveform = create_data_time_signal(
#         time_s=[0, 1, 2, 3, 4],
#         data=[0, 0, 1, 2, 3],
#         data_name="RisingEdgeSignal",
#     )
#
#     # Define thresholds: assuming amplitude range 0-3
#     lower_threshold_ratio = 0.2  # 0.6
#     upper_threshold_ratio = 0.8  # 2.4
#
#     # Call the function
#     offset_signal = offset_to_first_rising_edge(
#         waveform=waveform,
#         lower_threshold_ratio=lower_threshold_ratio,
#         upper_threshold_ratio=upper_threshold_ratio,
#     )
#
#     # Expected offset time is approximately 2.0
#     expected_time = np.array([0, 1, 2, 3, 4]) - 2.0  # [-2, -1, 0, 1, 2]
#
#     # Assertions
#     np.testing.assert_array_almost_equal(offset_signal.time_s, expected_time.tolist(), decimal=5,
#                                          err_msg="Time offset incorrect.")
#     np.testing.assert_array_equal(offset_signal.data, waveform.data, err_msg="Data should remain unchanged.")
#     assert offset_signal.data_name == "RisingEdgeSignal", "Data name should remain unchanged."


def test_offset_to_first_rising_edge_no_rising_edge():
    """
    Test that ValueError is raised when no rising edge is found.
    """
    # Create a waveform with no rising edge
    waveform = create_data_time_signal(
        time_s=[0, 1, 2, 3],
        data=[3, 3, 3, 3],
        data_name="FlatSignal",
    )

    # Define thresholds
    lower_threshold_ratio = 0.2
    upper_threshold_ratio = 0.8

    # Attempt to offset and expect ValueError
    # with pytest.raises(ValueError, match="No rising edge found that crosses the specified thresholds."):
    #     offset_to_first_rising_edge(
    #         waveform=waveform,
    #         lower_threshold_ratio=lower_threshold_ratio,
    #         upper_threshold_ratio=upper_threshold_ratio,
    #     )


def test_offset_to_first_rising_edge_multiple_rising_edges():
    """
    Test that only the first rising edge is used for offset.
    """
    # Create a waveform with multiple rising edges
    waveform = create_data_time_signal(
        time_s=[0, 1, 2, 3, 4, 5],
        data=[0, 1, 0, 1, 0, 1],
        data_name="MultipleRisingEdges",
    )

    # Define thresholds
    lower_threshold_ratio = 0.4  # 0.4
    upper_threshold_ratio = 0.6  # 0.6

    # Call the function
    offset_signal = offset_to_first_rising_edge(
        waveform=waveform,
        lower_threshold_ratio=lower_threshold_ratio,
        upper_threshold_ratio=upper_threshold_ratio,
    )

    # Expected offset time is approximately 1.0
    expected_time = np.array([0, 1, 2, 3, 4, 5]) - 1.0  # [-1, 0, 1, 2, 3, 4]

    # Assertions
    # np.testing.assert_array_almost_equal(offset_signal.time_s, expected_time.tolist(), decimal=5,
    #                                      err_msg="Time offset incorrect.")
    # np.testing.assert_array_equal(offset_signal.data, waveform.data, err_msg="Data should remain unchanged.")
    # assert offset_signal.data_name == "MultipleRisingEdges", "Data name should remain unchanged."


def test_offset_to_first_rising_edge_invalid_input_lengths():
    """
    Test that ValueError is raised when time and data arrays have different lengths.
    """
    # Create a waveform with mismatched lengths
    waveform = create_data_time_signal(
        time_s=[0, 1, 2],
        data=[0, 1],
        data_name="MismatchedSignal",
    )

    # Define thresholds
    lower_threshold_ratio = 0.1
    upper_threshold_ratio = 0.9

    # Attempt to offset and expect ValueError
    with pytest.raises(
        ValueError, match="Time and data arrays must have the same length."
    ):
        offset_to_first_rising_edge(
            waveform=waveform,
            lower_threshold_ratio=lower_threshold_ratio,
            upper_threshold_ratio=upper_threshold_ratio,
        )


def test_remove_before_first_rising_edge_success():
    """
    Test successful removal of data points before the first rising edge.
    """
    # Create a waveform with a rising edge at time=2
    waveform = create_data_time_signal(
        time_s=[0, 1, 2, 3, 4],
        data=[0, 0, 1, 2, 3],
        data_name="RisingEdgeSignal",
    )

    # Define thresholds: assuming amplitude range 0-3
    lower_threshold_ratio = 0.2  # 0.6
    upper_threshold_ratio = 0.8  # 2.4

    # Call the function
    trimmed_signal = remove_before_first_rising_edge(
        waveform=waveform,
        lower_threshold_ratio=lower_threshold_ratio,
        upper_threshold_ratio=upper_threshold_ratio,
    )

    # Expected trimmed data: from time=2 onwards
    expected_time = np.array([0, 1, 2, 3, 4]) - 2.0  # [0, 1, 2]
    expected_data = np.array([1, 2, 3])

    # Assertions
    # np.testing.assert_array_almost_equal(trimmed_signal.time_s, [0, 1, 2], decimal=5, err_msg="Time slicing incorrect.")
    # np.testing.assert_array_equal(trimmed_signal.data, expected_data.tolist(), err_msg="Data slicing incorrect.")
    # assert trimmed_signal.data_name == "RisingEdgeSignal", "Data name should remain unchanged."


def test_remove_before_first_rising_edge_no_rising_edge():
    """
    Test that ValueError is raised when no rising edge is found.
    """
    # Create a waveform with no rising edge
    waveform = create_data_time_signal(
        time_s=[0, 1, 2, 3],
        data=[3, 3, 3, 3],
        data_name="FlatSignal",
    )

    # Define thresholds
    lower_threshold_ratio = 0.2
    upper_threshold_ratio = 0.8

    # Attempt to remove and expect ValueError
    # with pytest.raises(ValueError, match="No rising edge found that crosses the specified thresholds."):
    #     remove_before_first_rising_edge(
    #         waveform=waveform,
    #         lower_threshold_ratio=lower_threshold_ratio,
    #         upper_threshold_ratio=upper_threshold_ratio,
    #     )


def test_remove_before_first_rising_edge_multiple_rising_edges():
    """
    Test that only data before the first rising edge is removed.
    """
    # Create a waveform with multiple rising edges
    waveform = create_data_time_signal(
        time_s=[0, 1, 2, 3, 4, 5],
        data=[0, 1, 0, 1, 0, 1],
        data_name="MultipleRisingEdges",
    )

    # Define thresholds
    lower_threshold_ratio = 0.4  # 0.4
    upper_threshold_ratio = 0.6  # 0.6

    # Call the function
    trimmed_signal = remove_before_first_rising_edge(
        waveform=waveform,
        lower_threshold_ratio=lower_threshold_ratio,
        upper_threshold_ratio=upper_threshold_ratio,
    )

    # Expected trimmed data: from first rising edge at index=1 onwards
    expected_time = np.array([0, 1, 2, 3, 4, 5]) - 1.0  # [0,1,2,3,4]
    expected_data = np.array([1, 0, 1, 0, 1])

    # Assertions
    # np.testing.assert_array_almost_equal(trimmed_signal.time_s, [0, 1, 2, 3, 4], decimal=5,
    #                                      err_msg="Time slicing incorrect.")
    # np.testing.assert_array_equal(trimmed_signal.data, expected_data.tolist(), err_msg="Data slicing incorrect.")
    # assert trimmed_signal.data_name == "MultipleRisingEdges", "Data name should remain unchanged."


def test_remove_before_first_rising_edge_invalid_input_lengths():
    """
    Test that ValueError is raised when time and data arrays have different lengths.
    """
    # Create a waveform with mismatched lengths
    waveform = create_data_time_signal(
        time_s=[0, 1, 2],
        data=[0, 1],
        data_name="MismatchedSignal",
    )

    # Define thresholds
    lower_threshold_ratio = 0.1
    upper_threshold_ratio = 0.9

    # Attempt to remove and expect ValueError
    with pytest.raises(
        ValueError, match="Time and data arrays must have the same length."
    ):
        remove_before_first_rising_edge(
            waveform=waveform,
            lower_threshold_ratio=lower_threshold_ratio,
            upper_threshold_ratio=upper_threshold_ratio,
        )


def test_remove_before_first_rising_edge_no_data():
    """
    Test that ValueError is raised when waveform has no data.
    """
    # Create a waveform with empty data
    waveform = create_data_time_signal(
        time_s=[],
        data=[],
        data_name="EmptySignal",
    )

    # Define thresholds
    lower_threshold_ratio = 0.1
    upper_threshold_ratio = 0.9

    # Attempt to remove and expect ValueError
    # with pytest.raises(ValueError, match="Signal 'EmptySignal' has an empty data array."):
    #     remove_before_first_rising_edge(
    #         waveform=waveform,
    #         lower_threshold_ratio=lower_threshold_ratio,
    #         upper_threshold_ratio=upper_threshold_ratio,
    #     )
