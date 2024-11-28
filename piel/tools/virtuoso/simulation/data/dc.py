from piel.types import SignalDCCollection, SignalTraceDC, SignalDC
from piel.conversion import read_csv_to_pandas
from .utils import sanitize_column_name


def dataframe_to_signal_dc_collection(df) -> SignalDCCollection:
    """
    Converts a DataFrame containing time and data columns into a `SignalDCCollection`.

    This function processes a DataFrame where each signal is represented by a pair of columns:
    one for input traces (time, ending with " X") and one for output traces (data, ending with " Y").
    It constructs `SignalDC` objects for each valid pair, grouping them into a `SignalDCCollection`.

    Args:
        df (pd.DataFrame): A DataFrame with columns representing input traces ('X') and output traces ('Y') pairs.

    Returns:
        SignalDCCollection: A collection of DC signals representing inputs and outputs.

    Example:
        Input DataFrame:
            /out (resistance=1000) X | /out (resistance=1000) Y | /out (resistance=2000) X | /out (resistance=2000) Y
            -------------------------|-------------------------|-------------------------|-------------------------
            0.0                      | 10.0                   | 0.0                    | 20.0
            1.0                      | 15.0                   | 1.0                    | 25.0

        Output:
            SignalDCCollection(
                inputs=[SignalDC(trace_list=[SignalTraceDC(name="out_resistance_1000_X", values=[0.0, 1.0]),
                                             SignalTraceDC(name="out_resistance_2000_X", values=[0.0, 1.0])])],
                outputs=[SignalDC(trace_list=[SignalTraceDC(name="out_resistance_1000_Y", values=[10.0, 15.0]),
                                              SignalTraceDC(name="out_resistance_2000_Y", values=[20.0, 25.0])])]
            )
    """
    inputs = []
    outputs = []

    # Loop through columns to identify "X" (input traces) and "Y" (output traces) pairs
    for col in df.columns:
        if col.endswith(" X"):
            base_name = col[:-2]  # Remove ' X'
            y_col = f"{base_name} Y"
            if y_col in df.columns:
                # Sanitize names
                input_name = sanitize_column_name(col)
                output_name = sanitize_column_name(y_col)

                # Create SignalTraceDC objects for input and output
                input_trace = SignalTraceDC(name=input_name, values=df[col].values)
                output_trace = SignalTraceDC(name=output_name, values=df[y_col].values)

                # Create SignalDC objects for inputs and outputs
                inputs.append(SignalDC(trace_list=[input_trace]))
                outputs.append(SignalDC(trace_list=[output_trace]))

    # Create and return the SignalDCCollection
    return SignalDCCollection(inputs=inputs, outputs=outputs, power=[])


def extract_signals_from_csv(file_path: str) -> SignalDCCollection:
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
    signals = dataframe_to_signal_dc_collection(df)

    return signals
