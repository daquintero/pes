# test_microstrip.py

import pytest
import numpy as np

# Import the functions to be tested from microstrip.py
from piel.models.physical.electrical.transmission_lines.microstrip import (
    epsilon_e,
    Z_0,
    alpha_c,
    R_s,
)

# Define the permeability of free space (mu_0) as per SI units
mu_0 = 4 * np.pi * 1e-7  # H/m


def test_epsilon_e_basic():
    """
    Test the epsilon_e function with typical input values.
    """
    epsilon_r = 4.4  # Relative permittivity for FR-4
    width_m = 1.0e-3  # 1 mm
    dielectric_thickness_m = 0.5e-3  # 0.5 mm

    expected_epsilon_e = (epsilon_r + 1) / 2 + (epsilon_r - 1) / 2 / np.sqrt(
        1 + 12 * dielectric_thickness_m / width_m
    )

    computed_epsilon_e = epsilon_e(epsilon_r, width_m, dielectric_thickness_m)

    assert computed_epsilon_e == pytest.approx(
        expected_epsilon_e, rel=1e-5
    ), f"Expected ε_e ≈ {expected_epsilon_e}, got {computed_epsilon_e}"


def test_Z_0_basic():
    """
    Test the Z_0 function with typical input values.
    """
    width_m = 1.0e-3  # 1 mm
    dielectric_thickness_m = 0.5e-3  # 0.5 mm
    epsilon_e_val = 2.5  # Example effective dielectric constant

    ratio = width_m / dielectric_thickness_m
    denominator = ratio + 1.393 + 0.667 * np.log(ratio + 1.444)
    expected_Z0 = 120 * np.pi / (np.sqrt(epsilon_e_val) * denominator)

    computed_Z0 = Z_0(width_m, dielectric_thickness_m, epsilon_e_val)

    assert computed_Z0 == pytest.approx(
        expected_Z0, rel=1e-5
    ), f"Expected Z₀ ≈ {expected_Z0} Ohms, got {computed_Z0} Ohms"


def test_alpha_c_basic():
    """
    Test the alpha_c function with typical input values.
    """
    surface_resistance_ohms = 0.05  # Ohms
    characteristic_impedance_ohms = 50.0  # Ohms
    width_m = 1.0e-3  # 1 mm

    expected_alpha_c = 8.68588 * (
        surface_resistance_ohms / (characteristic_impedance_ohms * width_m)
    )

    computed_alpha_c = alpha_c(
        surface_resistance_ohms, characteristic_impedance_ohms, width_m
    )

    assert computed_alpha_c == pytest.approx(
        expected_alpha_c, rel=1e-5
    ), f"Expected α_c ≈ {expected_alpha_c} dB/m, got {computed_alpha_c} dB/m"


def test_R_s_basic():
    """
    Test the R_s function with typical input values.
    """
    frequency_Hz = 1e9  # 1 GHz
    conductivity_S_per_m = 5.8e7  # Conductivity of copper (S/m)

    expected_R_s = np.sqrt(2 * np.pi * frequency_Hz * mu_0 / (2 * conductivity_S_per_m))
    # Simplify the equation: sqrt(pi * frequency_Hz * mu_0 / conductivity_S_per_m)

    computed_R_s = R_s(frequency_Hz, conductivity_S_per_m, permeability_free_space=mu_0)

    assert computed_R_s == pytest.approx(
        expected_R_s, rel=1e-5
    ), f"Expected R_s ≈ {expected_R_s} Ohms, got {computed_R_s} Ohms"


def test_epsilon_e_zero_width():
    """
    Test the epsilon_e function with zero width to check for division by zero handling.
    """
    epsilon_r = 4.4
    width_m = 0.0  # Zero width
    dielectric_thickness_m = 0.5e-3

    with pytest.raises(ZeroDivisionError):
        epsilon_e(epsilon_r, width_m, dielectric_thickness_m)


# def test_Z_0_zero_dielec_thickness():
#     """
#     Test the Z_0 function with zero dielectric thickness to check for handling.
#     """
#     width_m = 1.0e-3
#     dielectric_thickness_m = 0.0  # Zero thickness
#     epsilon_e_val = 2.5
#
#     with pytest.raises(ValueError):
#         # Assuming that a zero dielectric thickness leads to a ValueError in the function
#         # If not, you may need to adjust the test accordingly
#         Z_0(width_m, dielectric_thickness_m, epsilon_e_val)


def test_alpha_c_zero_width():
    """
    Test the alpha_c function with zero width to check for division by zero handling.
    """
    surface_resistance_ohms = 0.05
    characteristic_impedance_ohms = 50.0
    width_m = 0.0  # Zero width

    with pytest.raises(ZeroDivisionError):
        alpha_c(surface_resistance_ohms, characteristic_impedance_ohms, width_m)


def test_R_s_zero_conductivity():
    """
    Test the R_s function with zero conductivity to check for division by zero handling.
    """
    frequency_Hz = 1e9
    conductivity_S_per_m = 0.0  # Zero conductivity

    with pytest.raises(ZeroDivisionError):
        R_s(frequency_Hz, conductivity_S_per_m, permeability_free_space=mu_0)


def test_R_s_zero_frequency():
    """
    Test the R_s function with zero frequency.
    """
    frequency_Hz = 0.0  # Zero frequency
    conductivity_S_per_m = 5.8e7  # Conductivity of copper

    expected_R_s = np.sqrt(2 * np.pi * frequency_Hz * mu_0 / (2 * conductivity_S_per_m))
    # sqrt(0) = 0

    computed_R_s = R_s(frequency_Hz, conductivity_S_per_m, permeability_free_space=mu_0)

    assert computed_R_s == pytest.approx(
        0.0, rel=1e-5
    ), f"Expected R_s ≈ 0 Ohms for zero frequency, got {computed_R_s} Ohms"
