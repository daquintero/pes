from typing import Any
from piel.types import MultiTimeSignalData, Unit
import numpy as np
import matplotlib.pyplot as plt
from piel.visual.plot.position import create_axes_per_figure
from piel.visual.plot.core import save
import logging

logger = logging.getLogger(__name__)


def plot_multi_data_time_signal_equivalent(
    multi_signal: MultiTimeSignalData,
    fig: Any = None,
    axs: Any = None,
    subplots_kwargs: dict = None,
    xlabel: str | Unit = None,
    ylabel: str | Unit = None,
    **kwargs,
):
    """
    Plots all rising edge signals on the same figure with a shared x-axis.

    Args:
        multi_signal (List[TimeSignalData]): List of rising edge signals.
        subplots_kwargs (dict): Keyword arguments to pass to create_axes_per_figure.

    Returns:
        None
    """
    x_correction = 1
    y_correction = 1

    if not multi_signal:
        raise ValueError("The multi_signal list is empty.")

    if xlabel is None:
        xlabel = r"Time $s$"
    elif isinstance(xlabel, str):
        pass
    elif isinstance(xlabel, Unit):
        x_correction = xlabel.base
        logger.warning(
            f"Data correction of 1/{x_correction} from unit definition {xlabel} will be applied on x-axis"
        )
        xlabel = xlabel.label

    if ylabel is None:
        ylabel = r"Voltage $V$"
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

    for signal in multi_signal:
        if (len(signal.time_s) == 0) or (signal.time_s is None):
            raise ValueError(f"Signal '{signal.data_name}' has an empty time_s array.")

        time = np.array(signal.time_s) / x_correction
        data = np.array(signal.data) / y_correction

        axs[0].plot(
            time,
            data,
            label=signal.data_name,
            color=plt.rcParams["axes.prop_cycle"].by_key()["color"][0],
        )

    fig.supxlabel(xlabel)
    fig.supylabel(ylabel)

    save(fig, **kwargs)

    return fig, axs
