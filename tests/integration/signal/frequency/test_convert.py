# test_network_conversion.py

import pytest
import skrf
import numpy as np

# Import the function to be tested from network_conversion.py
from piel.integration.signal.frequency.convert import convert_to_network_transmission
from piel.tools.skrf import convert_skrf_network_to_network_transmission
from piel.types import NetworkTransmission, FrequencyTransmissionModel

# Monkey patch the convert_skrf_network_to_network_transmission into the module
# so that the convert_to_network_transmission uses this test version
import sys
import types

current_module = sys.modules[__name__]
setattr(
    current_module,
    "convert_skrf_network_to_network_transmission",
    convert_skrf_network_to_network_transmission,
)

# Replace the imported function in network_conversion.py to use the local convert_skrf_network_to_network_transmission
# This is necessary because in the original code, it's imported from piel.tools.skrf.convert
# For testing purposes, we redefine it here

# Note: If network_conversion.py imports convert_skrf_network_to_network_transmission
# using a specific path, you might need to adjust the import or use other techniques.
# For simplicity, this example assumes that redefining it in the current module suffices.

# Test Cases


def test_convert_to_network_transmission_with_skf_network():
    """
    Test convert_to_network_transmission when input is a skrf.Network instance.
    """
    # Create a simple skrf.Network instance
    freq = skrf.Frequency(start=1, stop=10, npoints=10, unit="ghz")
    s_parameters = np.random.rand(10, 2, 2)  # Random S-parameters for a 2-port network
    network = skrf.Network(frequency=freq, s=s_parameters)

    # Call the function
    network_transmission = convert_to_network_transmission(network)

    # Assertions
    assert isinstance(
        network_transmission, NetworkTransmission
    ), "Output should be an instance of NetworkTransmission"


#
# def test_convert_to_network_transmission_with_non_skf_network():
#     """
#     Test convert_to_network_transmission when input is not a skrf.Network instance.
#     """
#     # Create an object that is not a skrf.Network
#     non_network_input = FrequencyTransmissionModel()  # Or any other object
#
#     # Call the function
#     network_transmission = convert_to_network_transmission(non_network_input)
#
#     # Assertions
#     assert isinstance(network_transmission, NetworkTransmission), \
#         "Output should be an instance of NetworkTransmission"
#
# def test_convert_to_network_transmission_with_none():
#     """
#     Test convert_to_network_transmission when input is None.
#     """
#     # Call the function with None
#     network_transmission = convert_to_network_transmission(None)
#
#     # Assertions
#     assert isinstance(network_transmission, NetworkTransmission), \
#         "Output should be an instance of NetworkTransmission"
#
# def test_convert_to_network_transmission_with_invalid_type():
#     """
#     Test convert_to_network_transmission when input is of an invalid type (e.g., integer).
#     """
#     # Create an invalid input
#     invalid_input = 12345
#
#     # Call the function
#     network_transmission = convert_to_network_transmission(invalid_input)
#
#     # Assertions
#     assert isinstance(network_transmission, NetworkTransmission), \
#         "Output should be an instance of NetworkTransmission"


def test_convert_to_network_transmission_with_empty_skf_network():
    """
    Test convert_to_network_transmission with an empty skrf.Network instance.
    """
    # Create an empty skrf.Network instance
    freq = skrf.Frequency(start=1, stop=1, npoints=1, unit="ghz")
    s_parameters = np.empty((1, 2, 2))  # Empty S-parameters
    network = skrf.Network(frequency=freq, s=s_parameters)

    # Call the function
    network_transmission = convert_to_network_transmission(network)

    # Assertions
    assert isinstance(
        network_transmission, NetworkTransmission
    ), "Output should be an instance of NetworkTransmission"
