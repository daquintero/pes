"""
This module provides a set of utilities for converting between common files measurement to facilitate the representation of information across different toolsets.
"""

from functools import partial
import jax.numpy as jnp
import numpy as np
import pandas as pd
from piel.types.core import ArrayTypes, PackageArrayType, TupleIntType
from piel.types.digital import AbstractBitsType, BitsType, LogicSignalsList


def convert_array_type(array: ArrayTypes, output_type: PackageArrayType):
    """
    Converts an array to the specified output type.

    Args:
        array (ArrayTypes): The input array which can be of type numpy.ndarray or jax.ndarray.
        output_type (PackageArrayType): The desired output type, which can be "qutip", "jax", "numpy", "list", "tuple", or a tuple of integers (TupleIntType).

    Returns:
        The converted array in the specified output type.

    Raises:
        ValueError: If the specified output type is not recognized or not supported.

    Examples:
        >>> convert_array_type(np.array([1, 2, 3]), "jax")
        DeviceArray([1, 2, 3], dtype=int32)

        >>> convert_array_type(jnp.array([1, 2, 3]), "numpy")
        array([1, 2, 3])

        >>> convert_array_type(np.array([1, 2, 3]), TupleIntType)
        (1, 2, 3)
    """
    if output_type == "qutip":
        import qutip

        if not isinstance(array, qutip.Qobj):
            array = qutip.Qobj(array)
    elif output_type == "jax":
        if not isinstance(array, jnp.ndarray):
            array = jnp.array(array)
    elif output_type == "numpy":
        if not isinstance(array, np.ndarray):
            array = np.array(array)
    elif output_type == "list":
        if not isinstance(array, list):
            array = array.tolist()
    elif output_type == "tuple":
        if not isinstance(array, tuple):
            array = tuple(array.tolist())
    elif output_type == TupleIntType:
        if isinstance(array, jnp.ndarray):
            array = tuple(array.tolist())
        if isinstance(array, tuple):
            # Check if the tuple is a tuple of integers
            if all(isinstance(i, int) for i in array):
                pass
            elif all(isinstance(i, list) for i in array):
                array = tuple(i[0] for i in array)
            else:
                raise ValueError("The tuple must be a tuple of integers.")
    elif output_type == "str":
        if not isinstance(array, str):
            array = "".join(str(value) for value in array)
    else:
        raise ValueError(
            "The output type must be either 'qutip', 'jax', 'numpy', 'list', 'tuple', TupleIntType, or 'str'."
        )
    return array


# Partially applied function for converting an array to a string.
convert_tuple_to_string = partial(convert_array_type, output_type="str")


def convert_2d_array_to_string(list_2D: list[list]) -> str:
    """
    Converts a 2D array of binary files into a single string of binary values.

    Args:
        list_2D (list[list]): A 2D array of binary files where each sublist contains a single binary value.

    Returns:
        str: A string of binary files.

    Examples:
        >>> convert_2d_array_to_string([[0], [0], [0], [1]])
        '0001'
    """
    binary_string = "".join(str(sublist[0]) for sublist in list_2D)
    return binary_string


def absolute_to_threshold(
    array: ArrayTypes,
    threshold: float = 1e-6,
    dtype_output: int | float | bool = int,
    output_array_type: PackageArrayType = "jax",
) -> PackageArrayType:
    """
    Converts an array of optical transmission values to single-bit digital signals based on a threshold.

    Args:
        array (ArrayTypes): The input array of any dimension representing optical transmission values.
        threshold (float, optional): The threshold value to determine the digital signal. Defaults to 1e-6.
        dtype_output (int | float | bool, optional): The desired files type for the output values. Defaults to int.
        output_array_type (PackageArrayType, optional): The desired output array type. Defaults to "jax".

    Returns:
        The array with values converted to digital signals (0 or 1) based on the threshold and specified output type.

    Raises:
        ValueError: If the input array is not a numpy or jax array.

    Examples:
        >>> absolute_to_threshold(jnp.array([1e-7, 0.1, 1.0]), threshold=1e-5, output_array_type="numpy")
        array([0, 1, 1])
    """
    if isinstance(array, (jnp.ndarray, np.ndarray)):
        array = jnp.array(array) if isinstance(array, np.ndarray) else array

        array = jnp.abs(array) > threshold
        array = array.astype(dtype_output)
        array = convert_array_type(array, output_array_type)
    else:
        raise ValueError("The array must be either a jax or numpy array.")

    return array


# Alias for the absolute_to_threshold function.
a2d = absolute_to_threshold


def convert_to_bits(bits: AbstractBitsType) -> BitsType:
    """
    Converts an AbstractBitsType to a BitsType (binary string format).

    Args:
        bits (AbstractBitsType): The digital bits to convert. Can be a string, bytes, or integer.

    Returns:
        BitsType: The converted bits in binary string format (without '0b' prefix).

    Raises:
        TypeError: If the input type is not supported.
    """
    if isinstance(bits, str):
        return bits  # Already in binary string format
    elif isinstance(bits, bytes):
        # Convert each byte to its binary representation
        return "".join(format(byte, "08b") for byte in bits)

    elif isinstance(bits, int):
        # Convert integer to binary (remove the '0b' prefix)
        return bin(bits)[2:]

    else:
        raise TypeError(
            "Unsupported type for bits conversion. Supported measurement are str, bytes, or int."
        )


def convert_dataframe_to_bits(
    dataframe: pd.DataFrame, ports_list: LogicSignalsList
) -> pd.DataFrame:
    """
    Converts specified integer columns in the dataframe to their binary string representations.

    Args:
        dataframe (pd.DataFrame): The simulation files as a Pandas dataframe.
        ports_list (LogicSignalsList): List of column names (connection) to convert to binary string format.

    Returns:
        pd.DataFrame: The dataframe with specified columns converted to binary string format.
    """

    def int_to_binary_string(value: int, bits: int) -> str:
        """
        Converts an integer to a binary string representation, padded with leading zeros to fit the specified number of bits.

        Args:
            value (int): The integer to convert.
            bits (int): The number of bits for the binary representation.

        Returns:
            str: The binary string representation of the integer.
        """
        return format(value, f"0{bits}b")

    # Determine the number of bits required to represent the maximum integer value in the DataFrame
    max_bits = (
        dataframe[ports_list]
        .apply(lambda col: int(col.dropna().astype(int).max()).bit_length())
        .max()
    )

    # Apply conversion only to the specified columns in ports_list
    binary_converted_data = (
        dataframe.copy()
    )  # Create a copy of the dataframe to avoid modifying the original files

    for port in ports_list:
        if port in binary_converted_data.columns:
            binary_converted_data[port] = binary_converted_data[port].apply(
                lambda x: int_to_binary_string(int(x), max_bits)
                if isinstance(x, (int, float))
                else x
            )
        else:
            raise ValueError(f"Port '{port}' not found in DataFrame columns")

    return binary_converted_data
