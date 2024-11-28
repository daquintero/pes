from typing import Any
from piel.types import TimeSignalData, Unit
import numpy as np
import matplotlib.pyplot as plt
from piel.visual.plot.position import create_axes_per_figure
from piel.visual.plot.core import save
import logging

logger = logging.getLogger(__name__)


def plot_time_signal_data(
    signal: TimeSignalData,
    fig: Any = None,
    axs: Any = None,
    subplots_kwargs: dict = None,
    xlabel: str | Unit = None,
    ylabel: str | Unit = None,
    title: str | Unit = None,
    **kwargs,
):
    """
    Plots a single time signal on a figure.

    Args:
        signal (TimeSignalData): The time signal to plot.
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

    if (len(signal.time_s) == 0) or (signal.time_s is None):
        raise ValueError("The signal's time_s array is None.")

    if xlabel is None:
        xlabel = signal.time_s_unit.label
        x_correction = signal.time_s_unit.base
    elif isinstance(xlabel, str):
        pass
    elif isinstance(xlabel, Unit):
        x_correction = xlabel.base
        logger.warning(
            f"Data correction of 1/{x_correction} from unit definition {xlabel} will be applied on x-axis"
        )
        xlabel = xlabel.label

    if ylabel is None:
        ylabel = signal.data_unit.label
        y_correction = signal.data_unit.base
    elif isinstance(ylabel, str):
        pass
    elif isinstance(ylabel, Unit):
        y_correction = ylabel.base
        logger.warning(
            f"Data correction of 1/{y_correction} from unit definition {ylabel} will be applied on y-axis."
        )
        ylabel = ylabel.label

    if subplots_kwargs is None:
        subplots_kwargs = {}

    if (fig is None) or (axs is None):
        fig, axs = create_axes_per_figure(rows=1, columns=1, **subplots_kwargs)
    elif fig is None or axs is None:
        raise ValueError("Both fig and ax should be provided together or left as None.")

    if title is None:
        pass
    else:
        fig.suptitle(title)

    ax = axs[0]

    time = np.array(signal.time_s) / x_correction
    data = np.array(signal.data) / y_correction

    ax.plot(
        time,
        data,
        label=signal.data_name,
        color=plt.rcParams["axes.prop_cycle"].by_key()["color"][0],
    )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

    save(fig, **kwargs)

    return fig, ax
