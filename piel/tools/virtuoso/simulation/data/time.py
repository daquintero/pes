from piel.types import MultiDataTimeSignal, DataTimeSignalData
from piel.conversion import read_csv_to_pandas
from .utils import sanitize_column_name


def dataframe_to_multi_time_signal_data(df) -> MultiDataTimeSignal:
    """
    Converts a DataFrame containing time and data columns into a list of `DataTimeSignalData` objects.

    This function processes a DataFrame where each signal is represented by a pair of columns:
    one for time (ending with " X") and one for the corresponding data values (ending with " Y").
    It constructs `DataTimeSignalData` objects for each valid pair and returns them as a list.

    Args:
        df (pd.DataFrame): A DataFrame with columns representing time ('X') and data ('Y') pairs.

    Returns:
        MultiDataTimeSignal: A list of `DataTimeSignalData` objects, where each object represents a signal.

    Example:
        Input DataFrame:
            Signal1 X | Signal1 Y | Signal2 X | Signal2 Y
            --------- | --------- | --------- | ---------
            0.0       | 10.0      | 0.0       | 20.0
            1.0       | 15.0      | 1.0       | 25.0

        Output:
            [
                DataTimeSignalData(time_s=[0.0, 1.0], data=[10.0, 15.0], data_name="Signal1"),
                DataTimeSignalData(time_s=[0.0, 1.0], data=[20.0, 25.0], data_name="Signal2")
            ]
    """
    import re

    signals = []

    # Loop through columns to identify "X" (time) and "Y" (data) pairs
    for col in df.columns:
        if col.endswith(" X"):
            # Determine the base name of the signal
            base_name = col[:-2]  # Remove ' X'
            y_col = f"{base_name} Y"
            if y_col in df.columns:
                # Generate a valid data_name by sanitizing the base name
                data_name = sanitize_column_name(y_col)

                # Create a DataTimeSignalData object for the identified signal
                signal = DataTimeSignalData(
                    time_s=df[col].values,
                    data=df[y_col].values,
                    data_name=data_name,
                )
                signals.append(signal)

    return signals


def extract_signals_from_csv(file_path: str) -> MultiDataTimeSignal:
    """
    Reads a CSV file and extracts time-series signals as a list of `DataTimeSignalData` objects.

    This function reads the contents of a CSV file into a pandas DataFrame, then converts
    the DataFrame into a list of `DataTimeSignalData` objects using the `dataframe_to_multi_time_signal_data` function.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        MultiDataTimeSignal: A list of `DataTimeSignalData` objects, where each object represents a time-series signal.

    Example:
        If the CSV contains:
            Signal1 X,Signal1 Y,Signal2 X,Signal2 Y
            0.0,10.0,0.0,20.0
            1.0,15.0,1.0,25.0

        The output will be:
            [
                DataTimeSignalData(time_s=[0.0, 1.0], data=[10.0, 15.0], data_name="Signal1"),
                DataTimeSignalData(time_s=[0.0, 1.0], data=[20.0, 25.0], data_name="Signal2")
            ]
    """
    # Read the CSV file into a DataFrame
    df = read_csv_to_pandas(file_path)

    # Convert the DataFrame into a list of DataTimeSignalData objects
    signals = dataframe_to_multi_time_signal_data(df)

    return signals
