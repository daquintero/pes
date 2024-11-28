from typing import Any
from piel.types import Unit
import numpy as np
from piel.types import SignalDCCollection
from piel.visual.plot.position import create_axes_per_figure
from piel.visual.plot.core import save
import logging

logger = logging.getLogger(__name__)


def plot_signal_dc_collection_equivalent(
    signal_dc_collection: SignalDCCollection,
    fig: Any = None,
    axs: Any = None,
    xlabel: str | Unit = None,
    ylabel: str | Unit = None,
    title: str | Unit = None,
    labels: list[str] = None,
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
        pass
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
        pass
        y_correction = 1

    if subplots_kwargs is None:
        subplots_kwargs = {}

    if plot_kwargs is None:
        plot_kwargs = {"marker": "o", "linestyle": "-"}

    # Create a figure and axes if not provided
    if fig is None or axs is None:
        fig, axs = create_axes_per_figure(rows=1, columns=1, **subplots_kwargs)

    ax = axs[0]

    i = 0
    # Iterate through inputs and outputs to plot them
    for input_signal, output_signal in zip(
        signal_dc_collection.inputs, signal_dc_collection.outputs
    ):
        for input_trace, output_trace in zip(
            input_signal.trace_list, output_signal.trace_list
        ):
            # Apply unit corrections
            x_values = np.array(input_trace.values) / x_correction
            y_values = np.array(output_trace.values) / y_correction

            if labels is None:
                label_i = f"{input_trace.name} -> {output_trace.name}"
            else:
                label_i = labels[i]

            # Plot data
            ax.plot(x_values, y_values, label=label_i, **plot_kwargs)
        i += 1

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        fig.suptitle(title)

    ax.legend()

    # Save the figure using the save function and additional kwargs
    save(fig, **kwargs)

    return fig, ax
