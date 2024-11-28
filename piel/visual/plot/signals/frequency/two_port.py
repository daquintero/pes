from typing import Optional, Tuple
import numpy as np

import piel.types.units
from piel.types import NetworkTransmission
from piel.visual.plot.core import save
from piel.visual.plot.basic import plot_simple
from piel.visual.plot.position import create_axes_per_figure
import matplotlib.figure as mpl_fig
import matplotlib.axes as mpl_axes
import logging

logger = logging.getLogger(__name__)


def plot_s21_gain_per_input_power_dBm(
    network_transmission: NetworkTransmission,
    fig: Optional[mpl_fig.Figure] = None,
    axs: Optional[mpl_axes.Axes] = None,
    label: Optional[str] = None,
    xlabel: str = None,
    ylabel: str = None,
    **kwargs,
) -> tuple[mpl_fig.Figure, mpl_axes.Axes]:
    """
    Plots input power (p_in_dbm) vs S21 gain (s_21_db) from a NetworkTransmission object.

    Parameters:
    -----------
    frequency_array_state : NetworkTransmission
        The NetworkTransmission object containing the measurement data.

    fig : matplotlib.figure.Figure, optional
        The figure object to plot on. If None, a new figure is created.

    axs : matplotlib.axes.Axes, optional
        The axes object to plot on. If None, a new set of axes is created.

    label : str, optional
        The label for the plot. If None, a default label is used.

    Returns:
    --------
    tuple
        A tuple containing the matplotlib Figure and Axes objects.
    """
    # Create axes if not provided
    if (fig is None) or (axs is None):
        fig, axs = create_axes_per_figure(rows=1, columns=1)

    if xlabel is None:
        xlabel = r"$P_{in}$ $dBm$"

    if ylabel is None:
        ylabel = r"$S_{21}$ $dB$"

    # Extract input power in dBm from ScalarSource.input.magnitude
    try:
        p_in_dbm = np.array(network_transmission.input.magnitude)
    except AttributeError as e:
        logger.error(
            f"Failed to extract 'p_in_dbm' from NetworkTransmission.input.phasor.magnitude: {network_transmission}"
        )
        raise e

    # Initialize s_21_db as None
    s_21_db = None

    # Iterate through network transmissions to find S21
    for path_transmission in network_transmission.network:
        if path_transmission.connection == ("in0", "out0"):
            # Compute magnitude in dB from complex transmission
            transmission = np.array(path_transmission.transmission.magnitude)
            # Avoid log of zero by adding a small epsilon
            # Convert if linear units
            # epsilon = 1e-12
            # s_21_db = 20 * np.log10(np.abs(transmission) + epsilon)
            s_21_db = transmission
            break

    if s_21_db is None:
        logger.error(
            "S21 transmission ('in0', 'out0') not found in NetworkTransmission.network."
        )
        raise ValueError("S21 transmission ('in0', 'out0') not found.")

    # Determine label
    plot_label = label if label is not None else "S21 Magnitude"

    # Plot the data
    fig, axs = plot_simple(
        p_in_dbm,
        s_21_db,
        fig=fig,
        axs=axs,
        xlabel=xlabel,
        ylabel=ylabel,
        label=plot_label,
        **kwargs,
    )

    save(fig, **kwargs)

    return fig, axs


def plot_s11_magnitude_per_input_frequency(
    network_transmission: NetworkTransmission,
    fig: Optional[mpl_fig.Figure] = None,
    axs: Optional[mpl_axes.Axes] = None,
    label: str = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> Tuple[mpl_fig.Figure, mpl_axes.Axes]:
    """
    Plots S11 magnitudes vs input power (P_in_dBm) from a NetworkTransmission object on the same axes.

    Parameters:
    -----------
    network_transmission : NetworkTransmission
        The NetworkTransmission object containing the measurement data.

    fig : matplotlib.figure.Figure, optional
        The figure object to plot on. If None, a new figure is created.

    axs : matplotlib.axes.Axes, optional
        The axes object to plot on. If None, a new set of axes is created.

    labels : tuple of str, optional
        A tuple containing labels for S21 and S11 plots. If None, defaults to ("S21 Gain", "S11 Magnitude").

    xlabel : str, optional
        The label for the x-axis. If None, defaults to "P_in dBm".

    ylabel : str, optional
        The label for the y-axis. If None, defaults to "Magnitude (dB)".

    **kwargs :
        Additional keyword arguments passed to the plot function.

    Returns:
    --------
    tuple
        A tuple containing the matplotlib Figure and Axes objects.
    """
    from piel.analysis.signals.frequency.core.extract import (
        extract_two_port_network_transmission_to_dataframe,
    )

    # Create axes if not provided
    if (fig is None) or (axs is None):
        fig, axs = create_axes_per_figure(rows=1, columns=1)

    # Set default labels if not provided
    if xlabel is None:
        xlabel = piel.types.units.GHz

    if ylabel is None:
        ylabel = piel.types.units.dB

    # Set default plot labels
    default_label = "S11 Magnitude"
    s11_label = label if label is not None else default_label

    dataframe = extract_two_port_network_transmission_to_dataframe(network_transmission)
    f_in_Hz = dataframe.frequency_Hz
    s11_db = dataframe.s_11_magnitude_dBm

    # Plot S11 on the same axes
    fig, axs = plot_simple(
        f_in_Hz,
        s11_db,
        fig=fig,
        axs=[axs[0]],
        label=s11_label,
        xlabel=xlabel,
        ylabel=ylabel,
        **kwargs,
    )

    # Add legend to distinguish S21 and S11
    axs[0].legend(loc="lower right")

    # Save the figure if needed
    save(fig, **kwargs)

    return fig, axs


def plot_s21_magnitude_per_input_frequency(
    network_transmission: NetworkTransmission,
    fig: Optional[mpl_fig.Figure] = None,
    axs: Optional[mpl_axes.Axes] = None,
    label: Optional[Tuple[str, str]] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> Tuple[mpl_fig.Figure, mpl_axes.Axes]:
    """
    Plots S21 and S11 magnitudes vs input power (P_in_dBm) from a NetworkTransmission object on the same axes.

    Parameters:
    -----------
    network_transmission : NetworkTransmission
        The NetworkTransmission object containing the measurement data.

    fig : matplotlib.figure.Figure, optional
        The figure object to plot on. If None, a new figure is created.

    axs : matplotlib.axes.Axes, optional
        The axes object to plot on. If None, a new set of axes is created.

    labels : tuple of str, optional
        A tuple containing labels for S21 and S11 plots. If None, defaults to ("S21 Gain", "S11 Magnitude").

    xlabel : str, optional
        The label for the x-axis. If None, defaults to "P_in dBm".

    ylabel : str, optional
        The label for the y-axis. If None, defaults to "Magnitude (dB)".

    **kwargs :
        Additional keyword arguments passed to the plot function.

    Returns:
    --------
    tuple
        A tuple containing the matplotlib Figure and Axes objects.
    """
    from piel.analysis.signals.frequency.core.extract import (
        extract_two_port_network_transmission_to_dataframe,
    )

    # Create axes if not provided
    if (fig is None) or (axs is None):
        fig, axs = create_axes_per_figure(rows=1, columns=1)

    # Set default labels if not provided
    if xlabel is None:
        xlabel = piel.types.units.GHz

    if ylabel is None:
        ylabel = piel.types.units.dB

    # Set default plot labels
    default_label = "S21 Magnitude"
    s21_label = label if label is not None else default_label

    dataframe = extract_two_port_network_transmission_to_dataframe(network_transmission)
    f_in_Hz = dataframe.frequency_Hz
    if kwargs.get("bug_patch", True):
        s21_db = (
            dataframe.s_12_magnitude_dBm
        )  # TODO FIX THIS BUT HOW? Something is weird somewhere
    else:
        s21_db = dataframe.s_21_magnitude_dBm

    # Plot S21
    fig, axs = plot_simple(
        f_in_Hz,
        s21_db,
        fig=fig,
        axs=[axs[0]],
        xlabel=xlabel,
        ylabel=ylabel,
        label=s21_label,
        **kwargs,
    )

    # Add legend to distinguish S21 and S11
    axs[0].legend(loc="lower right")

    # Save the figure if needed
    save(fig, **kwargs)

    return fig, axs


def plot_s11_s21_magnitude_per_input_frequency(
    network_transmission: NetworkTransmission,
    fig: Optional[mpl_fig.Figure] = None,
    axs: Optional[mpl_axes.Axes] = None,
    labels: Optional[Tuple[str, str]] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> Tuple[mpl_fig.Figure, mpl_axes.Axes]:
    """
    Plots S21 and S11 magnitudes vs input power (P_in_dBm) from a NetworkTransmission object on the same axes.

    Parameters:
    -----------
    network_transmission : NetworkTransmission
        The NetworkTransmission object containing the measurement data.

    fig : matplotlib.figure.Figure, optional
        The figure object to plot on. If None, a new figure is created.

    axs : matplotlib.axes.Axes, optional
        The axes object to plot on. If None, a new set of axes is created.

    labels : tuple of str, optional
        A tuple containing labels for S21 and S11 plots. If None, defaults to ("S21 Gain", "S11 Magnitude").

    xlabel : str, optional
        The label for the x-axis. If None, defaults to "P_in dBm".

    ylabel : str, optional
        The label for the y-axis. If None, defaults to "Magnitude (dB)".

    **kwargs :
        Additional keyword arguments passed to the plot function.

    Returns:
    --------
    tuple
        A tuple containing the matplotlib Figure and Axes objects.
    """
    from piel.analysis.signals.frequency.core.extract import (
        extract_two_port_network_transmission_to_dataframe,
    )

    # Create axes if not provided
    if (fig is None) or (axs is None):
        fig, axs = create_axes_per_figure(rows=1, columns=1)

    # Set default labels if not provided
    if xlabel is None:
        xlabel = piel.types.units.GHz

    if ylabel is None:
        ylabel = piel.types.units.dB

    # Set default plot labels
    default_labels = ("S21 Magnitude", "S11 Magnitude")
    s21_label, s11_label = labels if labels is not None else default_labels

    dataframe = extract_two_port_network_transmission_to_dataframe(network_transmission)
    f_in_Hz = dataframe.frequency_Hz
    s11_db = dataframe.s_11_magnitude_dBm
    s21_db = dataframe.s_21_magnitude_dBm

    # Plot S11 on the same axes
    fig, axs = plot_simple(
        f_in_Hz,
        s11_db,
        fig=fig,
        axs=[axs[0]],
        label=s11_label,
        xlabel=xlabel,
        ylabel=ylabel,
        **kwargs,
    )

    # Plot S21
    fig, axs = plot_simple(
        f_in_Hz,
        s21_db,
        fig=fig,
        axs=[axs[0]],
        xlabel=xlabel,
        ylabel=ylabel,
        label=s21_label,
        **kwargs,
    )

    # Add legend to distinguish S21 and S11
    axs[0].legend(loc="lower right")

    # Save the figure if needed
    save(fig, **kwargs)

    return fig, axs
