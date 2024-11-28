import pandas as pd
from piel.experimental.devices.DPO73304 import (
    extract_measurement_to_dataframe,
    extract_waveform_to_dataframe,
    extract_to_data_time_signal,
)
from piel.types import (
    TimeSignalData,
)
from unittest.mock import patch, MagicMock


# Test extract_measurement_to_dataframe
def test_extract_measurement_to_dataframe():
    mock_csv_content = """1,2,3,4,5,6,name1,name2,name3"""
    mock_file = MagicMock()

    with patch("builtins.open", mock_file):
        with patch(
            "pandas.read_csv",
            return_value=pd.DataFrame(
                {
                    "value": [1],
                    "mean": [2],
                    "min": [3],
                    "max": [4],
                    "standard_deviation": [5],
                    "count": [6],
                    "name1": ["name1"],
                    "name2": ["name2"],
                    "name3": ["name3"],
                }
            ),
        ):
            df = extract_measurement_to_dataframe("dummy_path.csv")
            assert df.shape == (1, 7)
            assert "name" in df.columns
            assert df.loc[0, "name"] == "name1_name2_name3"


# Test extract_waveform_to_dataframe
def test_extract_waveform_to_dataframe():
    mock_csv_content = """1,2,3,4,5"""
    mock_file = MagicMock()

    with patch("builtins.open", mock_file):
        with patch(
            "pandas.read_csv",
            return_value=pd.DataFrame({"time_s": [1, 2], "voltage_V": [4, 5]}),
        ):
            df = extract_waveform_to_dataframe("dummy_path.csv")
            assert df.shape == (2, 2)
            assert "time_s" in df.columns
            assert "voltage_V" in df.columns


# Test extract_to_data_time_signal
def test_extract_to_data_time_signal():
    mock_csv_content = """1,2,3,4,5"""
    mock_file = MagicMock()

    with patch("builtins.open", mock_file):
        with patch(
            "pandas.read_csv",
            return_value=pd.DataFrame({"time_s": [1, 2, 3], "voltage_V": [4, 5, 6]}),
        ):
            signal = extract_to_data_time_signal("dummy_path.csv")
            assert isinstance(signal, TimeSignalData)
            assert signal.time_s.tolist() == [1, 2, 3]
            assert signal.data.tolist() == [4, 5, 6]
            assert signal.data_name == "voltage_V"


# Test extract_propagation_delay_data_from_measurement
def test_extract_propagation_delay_data_from_measurement():
    # mock_measurement = MagicMock(spec=PropagationDelayMeasurement)
    # mock_measurement.measurements_file = "dummy_measurement_file.csv"
    # mock_measurement.reference_waveform_file = "dummy_reference_waveform_file.csv"
    # mock_measurement.dut_waveform_file = "dummy_dut_waveform_file.csv"
    #
    # with patch("piel.return_path", return_value=MagicMock(exists=lambda: True)):
    #     with patch("piel.measurement.devices.DPO73304.extract_to_signal_measurement") as mock_extract_signal_measurement, \
    #          patch("piel.measurement.devices.DPO73304.extract_to_data_time_signal") as mock_extract_data_time_signal:
    #         mock_extract_signal_measurement.return_value = MagicMock(spec=SignalMetricsMeasurementCollection)
    #         mock_extract_data_time_signal.return_value = MagicMock(spec=TimeSignalData)
    #
    #         data = extract_propagation_delay_data_from_measurement(mock_measurement)
    #         assert isinstance(data, PropagationDelayMeasurementData)
    #         assert "measurements" in data.__dict__
    #         assert "reference_waveform" in data.__dict__
    #         assert "dut_waveform" in data.__dict__
    pass


# Test extract_to_signal_measurement
def test_extract_to_signal_measurement():
    mock_file = MagicMock()

    with patch("builtins.open", mock_file):
        with patch(
            "pandas.read_csv",
            return_value=pd.DataFrame(
                {
                    "name": ["test_signal"],
                    "value": [1],
                    "mean": [2],
                    "min": [3],
                    "max": [4],
                    "standard_deviation": [5],
                    "count": [6],
                }
            ),
        ):
            # signal_collection = extract_to_signal_measurement("dummy_path.csv")
            # assert isinstance(signal_collection, dict)
            # assert "test_signal" in signal_collection
            # assert isinstance(signal_collection["test_signal"], SignalMetricsData)
            pass


# Test combine_channel_data
def test_combine_channel_data():
    mock_file = MagicMock()

    with patch(
        "piel.experimental.devices.DPO73304.extract_to_data_time_signal"
    ) as mock_extract_to_data_time_signal:
        mock_extract_to_data_time_signal.return_value = MagicMock(spec=TimeSignalData)
        # signals = combine_channel_data(["dummy_path1.csv", "dummy_path2.csv"])
        #
        # assert isinstance(signals, list)
        # assert len(signals) == 2
        # assert all(isinstance(signal, TimeSignalData) for signal in signals)
        pass


# Add more tests as needed to cover additional scenarios and edge cases.
