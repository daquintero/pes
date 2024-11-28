import numpy as np


def effective_index_product(n_eff, L_nm, L_active, L_thermal):
    """
    Calculate the effective index product for a segment.

    Parameters:
    n_eff (float): Effective index of the material.
    L_nm (float): Non-modulated length of the segment (m).
    L_active (float): Active length of the segment (m).
    L_thermal (float): Thermal length of the segment (m).

    Returns:
    float: Effective index product.

    Formula:
    .. math::
        n_{eff, i} L_i = n_{eff, i} L_{nm, i} + n_{eff, i}(V) L_{active, i} + n_{eff, i}(T) L_{thermal, i}
    """
    return n_eff * L_nm + n_eff * L_active + n_eff * L_thermal


def relative_phase(phi2, phi1):
    """
    Calculate the relative phase difference.

    Parameters:
    phi2 (float): Phase at point 2 (radians).
    phi1 (float): Phase at point 1 (radians).

    Returns:
    float: Relative phase difference.

    Formula:
    .. math::
        \Delta \phi = \phi_2 - \phi_1
    """
    return phi2 - phi1


def phase_difference(n_eff2, L2, n_eff1, L1, wavelength):
    """
    Calculate the phase difference between two segments.

    Parameters:
    n_eff2 (float): Effective index of segment 2.
    L2 (float): Length of segment 2 (m).
    n_eff1 (float): Effective index of segment 1.
    L1 (float): Length of segment 1 (m).
    wavelength (float): Wavelength of light (m).

    Returns:
    float: Phase difference (radians).

    Formula:
    .. math::
        \Delta \phi = \frac{2 \pi (n_{eff, 2}L_2 - n_{eff, 1}L_1)}{\lambda_0}
    """
    return (2 * np.pi * (n_eff2 * L2 - n_eff1 * L1)) / wavelength


def balanced_mzi_phase_difference(delta_n_eff, L, wavelength):
    """
    Calculate the phase difference in a balanced Mach-Zehnder Interferometer (MZI).

    Parameters:
    delta_n_eff (float): Difference in effective indices between the arms.
    L (float): Arm length (m).
    wavelength (float): Wavelength of light (m).

    Returns:
    float: Phase difference (radians).

    Formula:
    .. math::
        \Delta \phi = \beta L = \frac{2 \pi \Delta n_{eff} L }{\lambda_0}
    """
    return (2 * np.pi * delta_n_eff * L) / wavelength


def free_spectral_range(wavelength, n_g, delta_L):
    """
    Calculate the free spectral range (FSR).

    Parameters:
    wavelength (float): Wavelength of light (m).
    n_g (float): Group index.
    delta_L (float): Path length difference (m).

    Returns:
    float: Free spectral range (m).

    Formula:
    .. math::
        FSR = \frac{\lambda^2}{n_{g} \Delta L}
    """
    return (wavelength**2) / (n_g * delta_L)


def insertion_loss(P_in_dBm, P_max_dBm):
    """
    Calculate the insertion loss of a device in decibels (dB).

    Parameters:
    P_in_dBm (float): Input power (dBm).
    P_max_dBm (float): Maximum transmitted power (dBm).

    Returns:
    float: Insertion loss (dB).

    Formula:
    .. math::
        IL = P_{in, dBm} - P_{max, dBm}
    """
    return P_in_dBm - P_max_dBm


def extinction_ratio(P_max, P_min):
    """
    Calculate the extinction ratio in decibels (dB).

    Parameters:
    P_max (float): Maximum power (W).
    P_min (float): Minimum power (W).

    Returns:
    float: Extinction ratio (dB).

    Formula:
    .. math::
        ER = 10 \cdot \log_{10} \left( \frac{P_{max}}{P_{min}} \right)
    """
    if P_min == 0:
        raise ValueError("Minimum power must be non-zero.")
    return 10 * np.log10(P_max / P_min)


def modulated_extinction_ratio(P_H, P_L):
    """
    Calculate the modulated extinction ratio in decibels (dB).

    Parameters:
    P_H (float): High power level (W).
    P_L (float): Low power level (W).

    Returns:
    float: Modulated extinction ratio (dB).

    Formula:
    .. math::
        ER_{mod} = 10 \cdot \log_{10} \left( \frac{P_{H}}{P_{L}} \right)
    """
    if P_L == 0:
        raise ValueError("Low power level must be non-zero.")
    return 10 * np.log10(P_H / P_L)
