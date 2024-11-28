from typing import Any
from piel.types import Unit
import numpy as np
from piel.types import SignalDCCollection
from piel.visual.plot.position import create_axes_per_figure
from piel.visual.plot.core import save
import logging

logger = logging.getLogger(__name__)


def plot_signal_dc_collection(
    signal_dc_collection: SignalDCCollection,
    fig: Any = None,
    axs: Any = None,
    xlabel: str | Unit = None,
    ylabel: str | Unit = None,
    title: str | Unit = None,
    subplots_kwargs: dict = None,
    plot_kwargs: dict = None,
    **kwargs,
):
    """
    Plots inputs vs outputs from a SignalDCCollection on a figure.

    Args:
        signal_dc_collection (SignalDCCollection): The collection of DC signals to plot.
        fig (matplotlib.figure.Figure, optional): Existing figure to plot on. If None, a new figure is created.
        axs (list[matplotlib.axes.Axes, optional]): Existing list of axes to plot on. If None, new axes are created. Plots on [0] by default.
        subplots_kwargs (dict, optional): Keyword arguments to pass to create_axes_per_figure.
        xlabel (str | Unit, optional): Label for the x-axis. If a Unit is provided, applies unit correction.
        ylabel (str | Unit, optional): Label for the y-axis. If a Unit is provided, applies unit correction.
        title (str | Unit, optional): Title for the plot.
        **kwargs: Additional keyword arguments to pass to the save function.

    Returns:
        tuple: A tuple containing the figure and axes objects.
    """

    # Extract input and output values
    input_values = []
    output_values = []

    for input_signal in signal_dc_collection.inputs:
        # for trace in input_signal.trace_list:
        input_values.extend(input_signal.trace_list[0].values)

    for output_signal in signal_dc_collection.outputs:
        output_values.extend(output_signal.trace_list[0].values)

    if len(input_values) == 0 or len(output_values) == 0:
        raise ValueError("Input or output signals are empty.")

    # Handle label units and corrections
    if xlabel is None:
        xlabel = "Input Signal"
        x_correction = 1
    elif isinstance(xlabel, Unit):
        x_correction = xlabel.base
        logger.warning(
            f"Data correction of 1/{x_correction} from unit {xlabel} applied on x-axis."
        )
        xlabel = xlabel.label
    else:
        xlabel = "Input Signal"
        x_correction = 1

    if ylabel is None:
        ylabel = "Output Signal"
        y_correction = 1
    elif isinstance(ylabel, Unit):
        y_correction = ylabel.base
        logger.warning(
            f"Data correction of 1/{y_correction} from unit {ylabel} applied on y-axis."
        )
        ylabel = ylabel.label
    else:
        ylabel = "Output Signal"
        y_correction = 1

    if subplots_kwargs is None:
        subplots_kwargs = {}

    if plot_kwargs is None:
        plot_kwargs = {"marker": "o", "linestyle": "-"}

    # Apply corrections if necessary
    input_values = np.array(input_values) / x_correction
    output_values = np.array(output_values) / y_correction

    # Create a figure and axes if not provided
    if fig is None or axs is None:
        fig, axs = create_axes_per_figure(rows=1, columns=1, **subplots_kwargs)

    ax = axs[0]

    # Plot the data
    ax.plot(input_values, output_values, **plot_kwargs)

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        fig.suptitle(title)

    ax.legend()

    # Save the figure using the save function and additional kwargs
    save(fig, **kwargs)

    return fig, ax
