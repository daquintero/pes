import pandas as pd
import numpy as np
from piel import return_path
from piel.types import (
    ElectroOpticDCPathTransmission,
    ElectroOpticDCNetworkTransmission,
    ElectroOpticDCMeasurementCollection,
    ConnectionTypes,
    PathTransmission,
    SignalDC,
    SignalTraceDC,
    V,
    A,
)


def fill_missing_pm_out(
    path_transmission: ElectroOpticDCPathTransmission, method: str = "linear"
) -> ElectroOpticDCPathTransmission:
    """
    Fills in missing `pm_out` (transmission) data in an ElectroOpticDCPathTransmission instance.

    Parameters:
    - path_transmission (ElectroOpticDCPathTransmission): The path transmission instance with potential missing transmission data.
    - method (str): The interpolation method to use. Default is 'linear'.
                    Other options include 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', etc.,
                    as supported by pandas' interpolate method.

    Returns:
    - ElectroOpticDCPathTransmission: A new instance with filled transmission data.

    Raises:
    - ValueError: If there are insufficient data points to perform interpolation.
    """
    # Extract voltage and transmission data
    signal_dc = path_transmission.input_dc
    transmission = path_transmission.output.transmission

    # Find the voltage trace
    voltage_trace = None
    for trace in signal_dc.trace_list:
        if trace.unit.datum.lower() in ["voltage"]:
            voltage_trace = trace
            break

    if voltage_trace is None:
        raise ValueError("No voltage trace found in SignalDC.")

    voltage_values = np.array(voltage_trace.values)
    transmission_values = np.array(transmission)

    # Check if transmission_values contains any np.nan
    if not np.isnan(transmission_values).any():
        # No missing data; return the original instance
        print("No missing transmission data found. Returning the original instance.")
        return path_transmission

    # Create a pandas DataFrame for easier handling
    df = pd.DataFrame({"bias_v": voltage_values, "pm_out": transmission_values})

    # Sort the DataFrame by voltage to ensure proper interpolation
    df_sorted = df.sort_values(by="bias_v").reset_index(drop=True)

    # Perform interpolation
    df_sorted["pm_out_filled"] = df_sorted["pm_out"].interpolate(
        method=method, limit_direction="both"
    )

    # Check if any np.nan remains after interpolation
    if df_sorted["pm_out_filled"].isnull().any():
        # If there are still NaNs, consider filling them with a fixed value or using a different method
        # Here, we'll forward-fill and backward-fill as a fallback
        df_sorted["pm_out_filled"] = (
            df_sorted["pm_out_filled"].fillna(method="ffill").fillna(method="bfill")
        )

        if df_sorted["pm_out_filled"].isnull().any():
            raise ValueError("Unable to fill all missing `pm_out` values.")

    # Update the transmission values with filled data
    filled_transmission = df_sorted["pm_out_filled"].tolist()

    # Create a new PathTransmission instance with filled data
    filled_path_transmission = PathTransmission(
        connection=path_transmission.output.connection, transmission=filled_transmission
    )

    # Compose a new ElectroOpticDCPathTransmission instance
    filled_electro_optic_dc_path_transmission = ElectroOpticDCPathTransmission(
        input_dc=signal_dc, output=filled_path_transmission
    )

    return filled_electro_optic_dc_path_transmission


def extract_electro_optic_dc_path_transmission_from_csv(
    file: str,
    port_map: ConnectionTypes,
    dc_voltage_column: str = "bias_v",
    dc_current_column: str = "bias_current",
    optical_power_column: str = "pm_out",
) -> ElectroOpticDCPathTransmission:
    """
    Converts a CSV file into an ElectroOpticDCPathTransmission instance.

    This function ensures that the output power (`pm_out`) aligns with the DC voltage (`bias_v`) and
    current (`bias_current`) data by inserting `np.nan` where `pm_out` data is missing.

    Parameters:
    - file (str): Path to the CSV file.
    - connection (ConnectionTypes): The port mapping information.
    - dc_voltage_column (str): The name of the DC voltage column in the CSV.
    - dc_current_column (str): The name of the DC current column in the CSV.
    - optical_power_column (str): The name of the optical power column in the CSV.

    Returns:
    - ElectroOpticDCPathTransmission: The mapped ElectroOpticDCPathTransmission instance.
    """
    # Ensure the file path is correctly resolved
    file = return_path(file)

    # Read the CSV file using pandas
    df = pd.read_csv(file)

    # Drop rows where essential columns (`bias_v` or `bias_current`) have missing values
    df_clean = df.dropna(subset=[dc_voltage_column, dc_current_column]).copy()

    # Handle the `pm_out` column:
    # Replace missing `pm_out` values with np.nan to maintain alignment
    if optical_power_column in df_clean.columns:
        # Ensure `pm_out` exists; if not, create it with all values as np.nan
        df_clean[optical_power_column] = df_clean[optical_power_column].astype(float)
    else:
        # If the column doesn't exist, create it with all values as np.nan
        df_clean[optical_power_column] = np.nan

    # Extract columns as lists
    bias_v_values = df_clean[dc_voltage_column].tolist()
    bias_current_values = df_clean[dc_current_column].tolist()
    pm_out_values = df_clean[optical_power_column].tolist()

    # Optionally, ensure that all lists have the same length
    # This should be guaranteed by the above operations, but adding a check
    # max_length = max(len(bias_v_values), len(bias_current_values), len(pm_out_values))
    if not (len(bias_v_values) == len(bias_current_values) == len(pm_out_values)):
        print(
            ValueError("Mismatch in lengths of extracted data columns. Appending Data")
        )

    # Create SignalTraceDC instances for bias_v and bias_current
    trace_bias_v = SignalTraceDC(
        unit=V,  # Voltage unit
        values=bias_v_values,
    )

    trace_bias_current = SignalTraceDC(
        unit=A,  # Current unit
        values=bias_current_values,
    )

    # Compose SignalDC with the traces
    signal_dc = SignalDC(trace_list=[trace_bias_v, trace_bias_current])

    # Create PathTransmission instance with pm_out
    path_transmission = PathTransmission(
        connection=port_map,
        transmission=pm_out_values,  # `pm_out` may contain np.nan
    )

    # Compose ElectroOpticDCPathTransmission with input and output
    electro_optic_dc_path_transmission = ElectroOpticDCPathTransmission(
        input_dc=signal_dc, output=path_transmission
    )

    electro_optic_dc_path_transmission = fill_missing_pm_out(
        path_transmission=electro_optic_dc_path_transmission
    )

    return electro_optic_dc_path_transmission


def extract_electro_optic_dc_network_from_measurement_collection(
    measurement_collection: ElectroOpticDCMeasurementCollection,
    dc_voltage_column: str = "bias_v",
    dc_current_column: str = "bias_current",
    optical_power_column: str = "pm_out",
) -> ElectroOpticDCNetworkTransmission:
    """
    Converts an ElectroOpticDCMeasurementCollection into an ElectroOpticDCNetworkTransmission instance.

    Parameters:
    - measurement_collection (ElectroOpticDCMeasurementCollection): The collection of measurements.
    - dc_voltage_column (str): Column name for DC voltage in the CSV files.
    - dc_current_column (str): Column name for DC current in the CSV files.
    - optical_power_column (str): Column name for optical power in the CSV files.

    Returns:
    - ElectroOpticDCNetworkTransmission: The compiled network transmission instance.
    """
    path_transmissions = []

    for measurement in measurement_collection.collection:
        # Extract the CSV file path and port mapping from the measurement
        csv_file = measurement.dc_transmission_file
        port_map = measurement.connection

        # Extract the ElectroOpticDCPathTransmission from the CSV
        path_transmission = extract_electro_optic_dc_path_transmission_from_csv(
            file=csv_file,
            port_map=port_map,
            dc_voltage_column=dc_voltage_column,
            dc_current_column=dc_current_column,
            optical_power_column=optical_power_column,
        )

        # Append to the list
        path_transmissions.append(path_transmission)

    # Create ElectroOpticDCNetworkTransmission with the list of path transmissions
    network_transmission = ElectroOpticDCNetworkTransmission(
        path_transmission_list=path_transmissions
    )

    return network_transmission
