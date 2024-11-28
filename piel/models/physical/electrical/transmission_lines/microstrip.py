import numpy as np
from piel.types.constants import mu_0


def epsilon_e(epsilon_r, width_m, dielectric_thickness_m):
    """
    Calculate the effective dielectric constant (ε_e) for a microstrip.

    The effective dielectric constant accounts for the field distribution
    between the microstrip and the substrate, influencing signal propagation.

    Parameters
    ----------
    epsilon_r : float
        Relative permittivity (dielectric constant) of the substrate.
    width_m : float
        Width of the microstrip line (meters).
    dielectric_thickness_m : float
        Thickness of the substrate (meters).

    Returns
    -------
    epsilon_e : float
        Effective dielectric constant.

    References
    ----------
    Equation (2):
        ε_e = (ε_r + 1)/2 + (ε_r - 1)/2 * 1/sqrt(1 + 12*dielectric_thickness_m/width_m)
    """
    epsilon_e = (epsilon_r + 1) / 2 + (epsilon_r - 1) / 2 / np.sqrt(
        1 + 12 * dielectric_thickness_m / width_m
    )
    return epsilon_e


def Z_0(width_m, dielectric_thickness_m, epsilon_e):
    """
    Calculate the characteristic impedance (Z₀) of a microstrip.

    The characteristic impedance represents the inherent resistance that
    the transmission line presents to the signal propagating through it.

    Parameters
    ----------
    width_m : float
        Width of the microstrip line (meters).
    dielectric_thickness_m : float
        Thickness of the substrate (meters).
    epsilon_e : float
        Effective dielectric constant of the microstrip.

    Returns
    -------
    characteristic_impedance_ohms : float
        Characteristic impedance in Ohms.

    References
    ----------
    Equation (1):
        Z₀ = 120π / [√ε_e * (width_m/dielectric_thickness_m + 1.393 + 0.667 ln(width_m/dielectric_thickness_m + 1.444))]
    """
    ratio = width_m / dielectric_thickness_m
    denominator = ratio + 1.393 + 0.667 * np.log(ratio + 1.444)
    characteristic_impedance_ohms = 120 * np.pi / (np.sqrt(epsilon_e) * denominator)
    return characteristic_impedance_ohms


def alpha_c(surface_resistance_ohms, characteristic_impedance_ohms, width_m):
    """
    Calculate the attenuation constant (α_c) in decibels per meter (dB/m).

    The attenuation constant measures how much signal is lost per meter due
    to resistive (ohmic) losses in the conductor of the microstrip line.

    Parameters
    ----------
    surface_resistance_ohms : float
        Surface resistance of the conductor (Ohms).
    characteristic_impedance_ohms : float
        Characteristic impedance of the microstrip (Ohms).
    width_m : float
        Width of the microstrip line (meters).

    Returns
    -------
    alpha_c : float
        Attenuation constant in dB/m.

    References
    ----------
    Equation (3):
        α_c (dB/m) = 8.68588 * (R_s / (Z₀ * width_m))
    """
    return 8.68588 * (
        surface_resistance_ohms / (characteristic_impedance_ohms * width_m)
    )


def R_s(frequency_Hz, conductivity_S_per_m, permeability_free_space=mu_0.value):
    """
    Calculate the surface resistivity (R_s) of a conductor at a given frequency.

    The surface resistivity is a measure of how much a conductor resists current
    flow along its surface, and it increases with frequency due to the skin effect.

    Parameters
    ----------
    frequency_Hz : float
        Frequency at which the resistivity is calculated (Hz).
    conductivity_S_per_m : float
        Electrical conductivity of the conductor (S/m).
    permeability_free_space : float, optional
        Permeability of free space (H/m). Default is the value from mu_0.

    Returns
    -------
    surface_resistance_ohms : float
        Surface resistivity in Ohms.

    Formula
    -------
    R_s = sqrt(ω * μ₀ / (2 * σ))

    Where:
    ω = 2π * frequency_Hz (angular frequency in rad/s)
    μ₀ = Permeability of free space (H/m)
    σ = Conductivity (S/m)
    """
    frequency_rad_s = 2 * np.pi * frequency_Hz
    return np.sqrt(
        frequency_rad_s * permeability_free_space / (2 * conductivity_S_per_m)
    )
