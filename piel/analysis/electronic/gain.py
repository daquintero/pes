import numpy as np


def calculate_voltage_gain_dB(v_in=1, v_out=1):
    """
    Calculate the voltage gain in decibels (dB).

    Parameters:
    v_in (float): Input voltage (V). Default is 1.
    v_out (float): Output voltage (V). Default is 1.

    Returns:
    float: Voltage gain in dB.

    Formula:
    .. math::
        G_V(dB) = 20 \cdot \log_{10} \left( \frac{V_{out}}{V_{in}} \right)
    """
    if v_in == 0 or v_out == 0:
        raise ValueError("Input and output voltage must be non-zero.")

    voltage_ratio = calculate_voltage_gain_ratio(v_in, v_out)
    return 20 * np.log10(voltage_ratio)


def calculate_voltage_gain_ratio(v_in=1, v_out=1):
    """
    Calculate the voltage gain ratio.

    Parameters:
    v_in (float): Input voltage (V). Default is 1.
    v_out (float): Output voltage (V). Default is 1.

    Returns:
    float: Voltage gain ratio.

    Formula:
    .. math::
        G_V = \frac{V_{out}}{V_{in}}
    """
    if v_in == 0:
        raise ValueError("Input voltage must be non-zero.")
    return v_out / v_in


def calculate_power_gain_50ohm_dB(v_in=1, v_out=1):
    """
    Calculate the power gain in decibels (dB) assuming a 50-ohm system.

    Parameters:
    v_in (float): Input voltage (V). Default is 1.
    v_out (float): Output voltage (V). Default is 1.

    Returns:
    float: Power gain in dB.

    Formula:
    .. math::
        G_P(dB) = 10 \cdot \log_{10} \left( \frac{V_{out}^2}{V_{in}^2} \right)

    Note:
    For a 50-ohm impedance, power is proportional to voltage squared.
    """
    if v_in == 0 or v_out == 0:
        raise ValueError("Input and output voltage must be non-zero.")
    return 10 * np.log10((v_out**2) / (v_in**2))


def calculate_power_gain_dB(p_in=1, p_out=1):
    """
    Calculate the power gain in decibels (dB).

    Parameters:
    p_in (float): Input power (W). Default is 1.
    p_out (float): Output power (W). Default is 1.

    Returns:
    float: Power gain in dB.

    Formula:
    .. math::
        G_P(dB) = 10 \cdot \log_{10} \left( \frac{P_{out}}{P_{in}} \right)
    """
    if p_in == 0 or p_out == 0:
        raise ValueError("Input and output power must be non-zero.")
    return 10 * np.log10(p_out / p_in)
