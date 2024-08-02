import pandas as pd
from typing import get_origin
from ..types import (
    PropagationDelayMeasurementCollection,
    PropagationDelayMeasurementDataCollection,
    PropagationDelayMeasurementData,
)
from ...types import (
    DataTimeSignalData,
    MultiDataTimeSignal,
    PathTypes,
    SignalMetricsData,
    SignalMetricsMeasurementCollection,
)


def extract_measurement_to_dataframe(file: PathTypes) -> pd.DataFrame:
    """
    Extracts the measurement files from a csv file and returns it as a pandas dataframe.

    Parameters
    ----------
    file : PathTypes
        The path to the csv file.

    Returns
    -------
    pd.DataFrame
        The measurement files as a pandas dataframe.
    """
    # TODO write here functionality to validate the file exists and it is a csv file in a particular structure compatible with a measurement.
    # TODO sort out actual measurement information
    dataframe = pd.read_csv(
        file,
        names=tuple(
            [
                "value",
                "mean",
                "min",
                "max",
                "standard_deviation",
                "count",
                "name1",
                "name2",
                "name3",
            ]
        ),
    )

    # Merge the name columns into a single column called 'name'
    dataframe["name"] = dataframe[["name1", "name2", "name3"]].apply(
        lambda x: " ".join(x.dropna().astype(str)), axis=1
    )

    # Drop the original name columns
    dataframe = dataframe.drop(columns=["name1", "name2", "name3"])

    # Convert all spaces to underscores in the 'name' column
    dataframe["name"] = dataframe["name"].str.replace(" ", "_")
    dataframe["name"] = dataframe["name"].str.replace("(", "_")
    dataframe["name"] = dataframe["name"].str.replace(")", "_")

    # Handle duplicate names by adding a prefix
    dataframe["name"] = dataframe["name"].apply(lambda x: x.lower())
    name_counts = dataframe["name"].value_counts()
    duplicates = name_counts[name_counts > 1].index

    for dup in duplicates:
        duplicate_indices = dataframe[dataframe["name"] == dup].index
        for i, idx in enumerate(duplicate_indices, 1):
            dataframe.at[idx, "name"] = f"{dup}_{i}"

    return dataframe


def extract_waveform_to_dataframe(file: PathTypes) -> pd.DataFrame:
    """
    Extracts the waveform files from a csv file and returns it as a pandas dataframe.

    Parameters
    ----------
    file : PathTypes
        The path to the csv file.

    Returns
    -------
    pd.DataFrame
        The waveform files as a pandas dataframe.
    """
    # TODO write here functionality to validate the file exists and it is a csv file in a particular structure
    return pd.read_csv(file, header=0, names=["time_s", "voltage_V"], usecols=[3, 4])


def extract_to_data_time_signal(
    file: PathTypes,
) -> DataTimeSignalData:
    """
    Extracts the waveform files from a csv file and returns it as a DataTimeSignal that can be used to analyse the signal with other methods.

    Parameters
    ----------
    file : PathTypes
        The path to the csv file.

    Returns
    -------
    DataTimeSignalData
        The waveform files as a DataTimeSignal.
    """
    dataframe = extract_waveform_to_dataframe(file)
    data_time_signal = DataTimeSignalData(
        time_s=dataframe.time_s.values,
        data=dataframe.voltage_V.values,
        data_name="voltage_V",
    )
    return data_time_signal


def extract_propagation_delay_measurement_sweep_data(
    propagation_delay_measurement_sweep: PropagationDelayMeasurementCollection,
) -> PropagationDelayMeasurementDataCollection:
    """
    This function is used to extract the relevant measurement files amd relate them to the sweep parameter. Because
    this function extracts multi-index files then we use xarray to analyze this files more clearly. It aims to extract all
    the files in the sweep file collection.
    """
    measurement_sweep_data = list()
    for (
        propagation_delay_measurement_i
    ) in propagation_delay_measurement_sweep.measurements:
        data_i = dict()
        if hasattr(propagation_delay_measurement_i, "measurements_file"):
            file = propagation_delay_measurement_i.measurements_file
            data_i["measurements"] = extract_to_signal_measurement(file)

        if hasattr(propagation_delay_measurement_i, "reference_waveform_file"):
            file = propagation_delay_measurement_i.reference_waveform_file
            data_i["reference_waveform"] = extract_to_data_time_signal(file)

        if hasattr(propagation_delay_measurement_i, "dut_waveform_file"):
            file = propagation_delay_measurement_i.dut_waveform_file
            data_i["dut_waveform"] = extract_to_data_time_signal(file)

        measurement_sweep_data.append(PropagationDelayMeasurementData(**data_i))

    assert isinstance(measurement_sweep_data, get_origin(PropagationDelayMeasurementDataCollection))
    return measurement_sweep_data


def extract_to_signal_measurement(
    file: PathTypes,
) -> SignalMetricsMeasurementCollection:
    """
    Extracts the measurement files from a csv file and returns it as a SignalMeasurement that can be used to analyse the signal.

    Parameters
    ----------
        file : PathTypes

    Returns
    -------
        SignalMetricsMeasurementCollection : dict[str, SignalMetricsData]
    """
    dataframe = extract_measurement_to_dataframe(file)
    signal_measurement_collection = dict()
    for _, row in dataframe.iterrows():
        signal_measurement_collection[row["name"]] = SignalMetricsData(
            value=row["value"],
            mean=row["mean"],
            min=row["min"],
            max=row["max"],
            standard_deviation=row["standard_deviation"],
            count=row["count"],
        )
    return signal_measurement_collection


def combine_channel_data(
    channel_file: list[PathTypes],
) -> MultiDataTimeSignal:
    """
    Extracts the waveform files from a list of csv files and returns it as a MultiDataTimeSignal that can be used to analyse the signals together.

    Parameters
    ----------
    channel_file : list[PathTypes]
        The list of paths to the csv files.

    Returns
    -------
    MultiDataTimeSignal
        The waveform files as a MultiDataTimeSignal.
    """
    multi_channel_data_time_signals = list()

    for file in channel_file:
        data_time_signal_i = extract_to_data_time_signal(file)
        multi_channel_data_time_signals.append(data_time_signal_i)

    return multi_channel_data_time_signals
