from piel.types import Phasor, PhasorTypes, NetworkTransmission
from piel.connectivity import get_port_index_from_name
import pandas as pd
from typing import Union, List
import numpy as np


def extract_phasor_to_dataframe(phasor: Phasor) -> pd.DataFrame:
    """
    Converts a Phasor instance into a pandas DataFrame with equivalent lengths for magnitude, phase, and frequency.

    Parameters:
    - input (Phasor): The Phasor instance to convert.

    Returns:
    - pd.DataFrame: A DataFrame containing magnitude, phase, and frequency columns with appropriate units.

    Raises:
    - TypeError: If the fields are of unsupported types.
    - ValueError: If the lengths of the fields do not match.
    """

    def to_list(
        field: Union[float, int, List[Union[float, int]], np.ndarray],
    ) -> List[Union[float, int]]:
        """
        Helper function to convert a field to a list.
        - Scalars are converted to single-element lists.
        - Lists and numpy arrays are converted to lists.
        """
        if isinstance(field, (float, int)):
            return [field]
        elif isinstance(field, (list, np.ndarray)):
            return list(field)
        else:
            raise TypeError(f"Unsupported type for field: {type(field)}")

    # Convert fields to lists
    magnitude = to_list(phasor.magnitude)
    phase = to_list(phasor.phase)
    frequency = to_list(phasor.frequency)

    # Check that all fields have the same length
    lengths = [len(magnitude), len(phase), len(frequency)]
    if not all(length == lengths[0] for length in lengths):
        raise ValueError(
            f"Fields have mismatched lengths: "
            f"magnitude ({len(magnitude)}), "
            f"phase ({len(phase)}), "
            f"frequency ({len(frequency)})"
        )

    # Define column names with units
    magnitude_col = f"magnitude_{phasor.magnitude_unit.shorthand}"
    phase_col = f"phase_{phasor.phase_unit.shorthand}"
    frequency_col = f"frequency_{phasor.frequency_unit.shorthand}"

    # Create DataFrame
    data = {magnitude_col: magnitude, phase_col: phase, frequency_col: frequency}

    df = pd.DataFrame(data)
    return df


def convert_complex_array_to_phasor_dataframe(
    complex_array: Union[List[complex], np.ndarray],
) -> pd.DataFrame:
    """
    Converts an array of complex numbers into a pandas DataFrame with magnitude, phase, and frequency.
    Sets frequency to 1 Hz for all entries.

    Parameters:
    - complex_array (List[complex] | np.ndarray): The array of complex numbers to convert.

    Returns:
    - pd.DataFrame: A DataFrame containing magnitude, phase, and frequency columns.

    Raises:
    - TypeError: If the input is not a list or numpy array of complex numbers.
    - ValueError: If the complex array is empty.
    """
    if isinstance(complex_array, list):
        if not all(isinstance(c, complex) for c in complex_array):
            raise TypeError("All elements in the list must be complex numbers.")
    elif isinstance(complex_array, np.ndarray):
        if not np.issubdtype(complex_array.dtype, np.complexfloating):
            raise TypeError("Numpy array must be of complex dtype.")
    else:
        raise TypeError(f"Unsupported type for complex_array: {type(complex_array)}")

    if len(complex_array) == 0:
        raise ValueError("complex_array must contain at least one complex number.")

    # Convert to numpy array for efficient computation
    complex_array = np.array(complex_array)

    # Calculate magnitude and phase (in degrees)
    magnitude = np.abs(complex_array)
    phase = np.angle(complex_array, deg=True)

    # Set frequency to 1 Hz for all entries
    frequency = np.ones_like(magnitude)

    # Define units
    magnitude_unit = "dBm"
    phase_unit = "degree"
    frequency_unit = "Hz"

    # Define column names with units
    magnitude_col = f"magnitude_{magnitude_unit}"
    phase_col = f"phase_{phase_unit}"
    frequency_col = f"frequency_{frequency_unit}"

    # Create DataFrame
    data = {magnitude_col: magnitude, phase_col: phase, frequency_col: frequency}

    df = pd.DataFrame(data)
    return df


def extract_phasor_type_to_dataframe(phasor_type: PhasorTypes) -> pd.DataFrame:
    """
    Converts any PhasorTypes instance into a pandas DataFrame.
    - If phasor_type is a Phasor instance, uses extract_phasor_to_dataframe.
    - If phasor_type is an array of complex numbers, converts to magnitude, phase, frequency=1.
    - If phasor_type is numerical (int or float), treats as scalar input with magnitude=phasor_type,
      phase=0, frequency=1.
    - If phasor_type is a list or numpy array of numerical types, treats as magnitude with phase=0 and frequency=1.

    Parameters:
    - phasor_type (PhasorTypes): The input type to convert.

    Returns:
    - pd.DataFrame: A DataFrame containing magnitude, phase, and frequency columns.

    Raises:
    - TypeError: If the phasor_type is of unsupported type.
    - ValueError: If input data is invalid.
    """
    if isinstance(phasor_type, Phasor):
        # Use the existing function
        return extract_phasor_to_dataframe(phasor_type)
    elif (
        isinstance(phasor_type, list)
        and all(isinstance(c, complex) for c in phasor_type)
    ) or (
        isinstance(phasor_type, np.ndarray)
        and np.issubdtype(phasor_type.dtype, np.complexfloating)
    ):
        # Use the complex array conversion function
        return convert_complex_array_to_phasor_dataframe(phasor_type)
    elif isinstance(phasor_type, (float, int)):
        # Treat as scalar input: magnitude=phasor_type, phase=0, frequency=1
        phasor = Phasor(magnitude=phasor_type, phase=0.0, frequency=1.0)
        return extract_phasor_to_dataframe(phasor)
    elif isinstance(phasor_type, (list, np.ndarray)):
        # Assume it's a magnitude array with phase=0 and frequency=1
        if isinstance(phasor_type, list):
            if not all(isinstance(m, (float, int)) for m in phasor_type):
                raise TypeError("List must contain numerical values.")
        elif isinstance(phasor_type, np.ndarray):
            if not np.issubdtype(phasor_type.dtype, np.number):
                raise TypeError("Numpy array must be of numerical dtype.")

        # Convert to list
        magnitude = phasor_type.tolist()
        length = len(magnitude)
        phasor = Phasor(
            magnitude=magnitude, phase=[0.0] * length, frequency=[1.0] * length
        )
        return extract_phasor_to_dataframe(phasor)
    else:
        raise TypeError(f"Unsupported PhasorType: {type(phasor_type)}")


def extract_two_port_network_transmission_to_dataframe(
    network_transmission: "NetworkTransmission",
) -> pd.DataFrame:
    """
    Converts a NetworkTransmission instance into a single pandas DataFrame that includes:
    - The main input data from NetworkTransmission.input.
    - The transmission input data from each PathTransmission in NetworkTransmission.network,
      with columns prefixed by the corresponding S-parameter name (e.g., s_11, s_21).

    This function is generalized to handle both integer-based port tuples (e.g., (0, 0))
    and string-based port tuples (e.g., ("in0", "out0")).

    Parameters:
    - network_transmission (NetworkTransmission): The NetworkTransmission instance to convert.

    Returns:
    - pd.DataFrame: A combined DataFrame containing the main input and all path transmission phasors.

    Raises:
    - TypeError: If any transmission input is of unsupported type.
    - ValueError: If any input data is invalid or if DataFrames have mismatched lengths.
    """
    # Convert the main input to DataFrame
    main_df = extract_phasor_type_to_dataframe(network_transmission.input)

    # Determine the starting index for S-parameters
    start_index = get_s_parameter_start_index(network_transmission)

    # Define the number of ports (assuming two-port network)
    num_ports = 2  # TODO update to automatic extraction

    i = 0
    for path_transmission in network_transmission.network:
        try:
            input_port, output_port = path_transmission.connection
            # print(input_port, output_port)
        except ValueError as e:
            raise ValueError(
                f"Invalid connection format: {path_transmission.connection}"
            ) from e

        # print("output, input")
        # print(output_port, input_port)

        input_index = get_port_index_from_name(input_port, starting_index=start_index)
        output_index = get_port_index_from_name(output_port, starting_index=start_index)

        # print("index")
        # print(output_index, input_index)

        # TODO still a bit hacked but how to fix better
        # TODO URGENT FIX properly implement
        if input_index == output_index == (i + 1):
            pass
        elif input_index != output_index:
            pass
        elif input_index == output_index:
            pass
        else:
            # S11, s21, s12, s22, ...
            input_index = (i // num_ports) + start_index + 1
            output_index = (i % num_ports) + start_index + 1

        # Construct the S-parameter string, e.g., "s_11", "s_21", etc.
        # print(input_index, output_index)
        s_parameter_str = f"s_{output_index}{input_index}"

        # print("s_parameter_str")
        # print(s_parameter_str)

        # Convert the transmission input to DataFrame
        path_df = extract_phasor_type_to_dataframe(path_transmission.transmission)

        # Prefix the columns with the S-parameter name
        path_df_prefixed = path_df.rename(
            columns=lambda x: f"{s_parameter_str}_{x.replace(' ', '_')}"
        )

        # Check if the lengths match before concatenation
        if len(main_df) != len(path_df_prefixed):
            raise ValueError(
                f"Length mismatch between main input ({len(main_df)}) and transmission input for S-parameter '{s_parameter_str}' ({len(path_df_prefixed)})."
            )

        # Concatenate the path DataFrame to the main DataFrame
        main_df = pd.concat([main_df, path_df_prefixed], axis=1)
        i += 1

    return main_df


def get_s_parameter_start_index(
    network_transmission: "NetworkTransmission",
) -> int:
    """
    Determines the starting index for S-parameters based on the port connectivity in the NetworkTransmission.

    It determines all the existing ports in all the connections and extracts the minimum port connectivity.
    Then, based on the minimum port index, it sets the starting index:
    - If the minimum port index is 0, starting_index is 0
    - If the minimum port index is 1, starting_index is 1
    - Otherwise, raises a ValueError

    Args:
        network_transmission (NetworkTransmission): The network transmission instance.

    Returns:
        int: The starting index (0 or 1).

    Raises:
        ValueError: If the minimum port index is not 0 or 1, or if no ports are found.
    """
    all_ports = []
    for path_transmission in network_transmission.network:
        try:
            # Attempt to unpack connection as a tuple (input_port, output_port)
            input_port, output_port = path_transmission.connection
            all_ports.extend([input_port, output_port])
        except ValueError as e:
            raise ValueError(
                f"Invalid connection format: {path_transmission.connection}"
            ) from e

    if not all_ports:
        raise ValueError("No ports found in network_transmission.")

    # Extract numerical port indices without adjusting for starting index
    port_numbers = []
    for port in all_ports:
        port_number = get_port_index_from_name(port, starting_index=None)
        port_numbers.append(port_number)

    # Determine starting index based on the minimum port number
    min_port = min(port_numbers)
    if min_port == 0:
        starting_index = 0
    elif min_port == 1:
        starting_index = 1
    else:
        raise ValueError(f"Unexpected minimum port index: {min_port}. Expected 0 or 1.")

    return starting_index
