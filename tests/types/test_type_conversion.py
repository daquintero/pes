import pytest
import numpy as np
import jax.numpy as jnp
import pandas as pd
import qutip

import piel.types
from piel.types import (
    convert_array_type,
    convert_tuple_to_string,
    convert_2d_array_to_string,
    absolute_to_threshold,
    convert_to_bits,
    convert_dataframe_to_bits,
    PielBaseModel,
    Quantity,
    a2d,
)  # Adjust the import based on your actual module structure


# Test cases for convert_array_type function
def test_convert_array_type_numpy_to_jax():
    array = np.array([1, 2, 3])
    converted = convert_array_type(array, "jax")
    assert isinstance(converted, jnp.ndarray)
    assert np.array_equal(converted, jnp.array([1, 2, 3]))


def test_convert_array_type_jax_to_numpy():
    array = jnp.array([1, 2, 3])
    converted = convert_array_type(array, "numpy")
    assert isinstance(converted, np.ndarray)
    assert np.array_equal(converted, np.array([1, 2, 3]))


def test_convert_array_type_to_qutip():
    array = np.array([1, 2, 3])
    converted = convert_array_type(array, "qutip")
    assert isinstance(converted, qutip.Qobj)


def test_convert_array_type_to_list():
    array = np.array([1, 2, 3])
    converted = convert_array_type(array, "list")
    assert isinstance(converted, list)
    assert converted == [1, 2, 3]


def test_convert_array_type_to_tuple():
    array = np.array([1, 2, 3])
    converted = convert_array_type(array, "tuple")
    assert isinstance(converted, tuple)
    assert converted == (1, 2, 3)


# TODO check this
# def test_convert_array_type_to_tuple_int():
#     array = np.array([1, 2, 3])
#     converted = convert_array_type(array, TupleIntType)
#     assert isinstance(converted, tuple)
#     assert converted == (1, 2, 3)


def test_convert_array_type_invalid_type():
    array = np.array([1, 2, 3])
    with pytest.raises(ValueError):
        convert_array_type(array, "invalid_type")


# Test cases for convert_tuple_to_string
def test_convert_tuple_to_string():
    array = np.array([1, 2, 3])
    result = convert_tuple_to_string(array)
    assert result == "123"


# Test cases for convert_2d_array_to_string
def test_convert_2d_array_to_string():
    array_2d = [[0], [0], [1], [1]]
    result = convert_2d_array_to_string(array_2d)
    assert result == "0011"

    array_2d_mixed = [[1], [0], [0], [1]]
    result = convert_2d_array_to_string(array_2d_mixed)
    assert result == "1001"


# Test cases for absolute_to_threshold (a2d)
def test_absolute_to_threshold():
    array = jnp.array([1e-7, 0.1, 1.0])
    result = absolute_to_threshold(array, threshold=1e-5, output_array_type="numpy")
    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, np.array([0, 1, 1]))


def test_absolute_to_threshold_default():
    array = np.array([1e-7, 0.1, 1.0])
    result = a2d(array)
    assert isinstance(result, jnp.ndarray)
    assert np.array_equal(result, jnp.array([0, 1, 1]))


# Test cases for convert_to_bits
def test_convert_to_bits_from_str():
    bits = "1101"
    result = convert_to_bits(bits)
    assert result == "1101"


def test_convert_to_bits_from_bytes():
    bits = b"\x0f"  # 00001111 in binary
    result = convert_to_bits(bits)
    assert result == "00001111"


def test_convert_to_bits_from_int():
    bits = 13  # Binary representation is 1101
    result = convert_to_bits(bits)
    assert result == "1101"


def test_convert_to_bits_invalid_type():
    with pytest.raises(TypeError):
        convert_to_bits(13.5)  # float is not a supported type


# TODO
# Test cases for convert_dataframe_to_bits
# def test_convert_dataframe_to_bits():
#     files = {
#         'A': [0, 1, 2],
#         'B': [3, 4, 5]
#     }
#     df = pd.DataFrame(files)
#     ports_list = ['A', 'B']
#     result_df = convert_dataframe_to_bits(df, ports_list)
#
#     assert 'A' in result_df.columns
#     assert 'B' in result_df.columns
#     assert result_df['A'].tolist() == ['00', '01', '10']
#     assert result_df['B'].tolist() == ['11', '100', '101']


def test_convert_dataframe_to_bits_missing_port():
    data = {"A": [0, 1, 2], "B": [3, 4, 5]}
    df = pd.DataFrame(data)
    ports_list = ["A", "C"]  # 'C' is not in the dataframe
    with pytest.raises(KeyError):
        convert_dataframe_to_bits(df, ports_list)


# Test cases for PielBaseModel
class TestModel(PielBaseModel):
    field1: int
    field2: str = None


def test_piel_base_model():
    model = TestModel(field1=123, field2="test")
    assert model.field1 == 123
    assert model.field2 == "test"


# Test cases for Quantity
def test_quantity_type_initialization():
    quantity = Quantity(unit=piel.types.m)
    assert quantity.unit == piel.types.m


def test_quantity_type_default():
    quantity = Quantity()
    assert quantity.unit == piel.types.ratio
