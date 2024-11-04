import numpy as np
import pandas as pd
from typing import List, Optional, Any
import logging
from piel.types import Unit
from .position import create_axes_per_figure
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def plot_simple(
    x_data: np.ndarray,
    y_data: np.ndarray,
    label: Optional[str] = None,
    ylabel: str | Unit | None = None,
    xlabel: str | Unit | None = None,
    fig: Optional[Any] = None,
    axs: Optional[List[Any]] = None,
    title: Optional[str] = None,
    plot_args: list = None,
    plot_kwargs: dict = None,
    figure_kwargs: dict = None,
    legend_kwargs: dict = None,
    title_kwargs: dict = None,
    xlabel_kwargs: dict = None,
    ylabel_kwargs: dict = None,
    *args,
    **kwargs,
) -> tuple:
    """
    Plot a simple line graph. This function abstracts the basic plotting functionality
    while keeping the flexibility of the matplotlib library, allowing customization of
    labels, titles, and figure properties.

    Args:
        x_data (np.ndarray): Data for the X-axis.
        y_data (np.ndarray): Data for the Y-axis.
        label (Optional[str], optional): Label for the plot line, useful for legends. Defaults to None.
        ylabel (str | Unit | None, optional): Label for the Y-axis, or a Unit object with a `label` and `base` attribute. Defaults to None.
        xlabel (str | Unit | None, optional): Label for the X-axis, or a Unit object with a `label` and `base` attribute. Defaults to None.
        fig (Optional[Any], optional): Matplotlib Figure object to be used. Defaults to None.
        axs (Optional[List[Any]], optional): List of Matplotlib Axes objects. Defaults to None.
        title (Optional[str], optional): Title of the plot. Defaults to None.
        plot_args (list, optional): Positional arguments passed to plt.plot(). Defaults to None.
        plot_kwargs (dict, optional): Keyword arguments passed to plt.plot(). Defaults to None.
        figure_kwargs (dict, optional): Keyword arguments for figure creation. Defaults to None.
        legend_kwargs (dict, optional): Keyword arguments for legend customization. Defaults to None.
        title_kwargs (dict, optional): Keyword arguments for title customization. Defaults to None.
        xlabel_kwargs (dict, optional): Keyword arguments for X-axis label customization. If 'show' is set to False, the X-axis label will not be displayed. Defaults to None.
        ylabel_kwargs (dict, optional): Keyword arguments for Y-axis label customization. If 'show' is set to False, the Y-axis label will not be displayed. Defaults to None.
        *args: Additional positional arguments for plt.plot().
        **kwargs: Additional keyword arguments for plt.plot().

    Returns:
        Tuple[plt.Figure, plt.Axes]: The figure and axes of the plot.

    """

    if figure_kwargs is None:
        figure_kwargs = {"tight_layout": True}

    if fig is None and axs is None:
        fig, axs = create_axes_per_figure(rows=1, columns=1, **figure_kwargs)

    if plot_kwargs is None:
        plot_kwargs = {"label": label} if label is not None else {}

    title_kwargs = title_kwargs or {}
    xlabel_kwargs = xlabel_kwargs or {"show": True}
    ylabel_kwargs = ylabel_kwargs or {"show": True}

    plot_args = plot_args or []

    # Handle xlabel unit correction
    x_correction = 1
    if xlabel and isinstance(xlabel, Unit):
        x_correction = xlabel.base
        xlabel = xlabel.label

    # Handle ylabel unit correction
    y_correction = 1
    if ylabel and isinstance(ylabel, Unit):
        y_correction = ylabel.base
        ylabel = ylabel.label

    # Plotting
    ax = axs[0]
    ax.plot(
        np.array(x_data) / x_correction,
        np.array(y_data) / y_correction,
        *plot_args,
        **plot_kwargs,
    )

    # Set x and y labels with keyword arguments if 'show' is not False
    if xlabel is not None and xlabel_kwargs.get("show", True):
        xlabel_kwargs.pop(
            "show", None
        )  # Remove 'show' from kwargs to avoid passing it to set_xlabel
        ax.set_xlabel(xlabel, **xlabel_kwargs)

    if ylabel is not None and ylabel_kwargs.get("show", True):
        ylabel_kwargs.pop(
            "show", None
        )  # Remove 'show' from kwargs to avoid passing it to set_ylabel
        ax.set_ylabel(ylabel, **ylabel_kwargs)

    # Set title with keyword arguments
    if title is not None:
        ax.set_title(title, **title_kwargs)

    # Add legend if label and legend_kwargs are provided
    if label is not None and legend_kwargs is not None:
        ax.legend(**legend_kwargs)

    # Rotate x-axis labels for better readability
    for xtick_label in ax.get_xticklabels():
        xtick_label.set_rotation(45)
        xtick_label.set_ha("right")

    return fig, axs


def plot_simple_multi_row(
    data: pd.DataFrame,
    x_axis_column_name: str = "t",
    row_list: Optional[List[str]] = None,
    y_label: Optional[List[str]] = None,
    x_label: Optional[str] = None,
    titles: Optional[List[str]] = None,
    subplot_spacing: float = 0.15,
) -> Any:
    """
    Plot multiple rows of files on separate subplots, sharing the same x-axis.

    Args:
        data (pd.DataFrame): Data to plot.
        x_axis_column_name (str, optional): Column name of the x-axis. Defaults to "t".
        row_list (Optional[List[str]], optional): List of column names to plot. Defaults to None.
        y_label (Optional[List[str]], optional): List of Y-axis titles for each subplot. Defaults to None.
        x_label (Optional[str], optional): Title of the x-axis. Defaults to None.
        titles (Optional[List[str]], optional): Titles for each subplot. Defaults to None.
        subplot_spacing (float, optional): Spacing between subplots. Defaults to 0.3.

    Returns:
        plt.Figure: The matplotlib figure containing the subplots.
    """
    import matplotlib.pyplot as plt

    if row_list is None:
        raise ValueError("row_list must be provided")

    x_data = data[x_axis_column_name]
    y_data_list = [data[row] for row in row_list]

    if y_label is None:
        y_label = row_list

    if titles is None:
        titles = [""] * len(row_list)

    row_amount = len(row_list)
    fig, axes = plt.subplots(row_amount, 1, sharex=True, figsize=(8, row_amount * 2))

    if row_amount == 1:
        axes = [axes]

    for _, (ax_i, y_data_i, y_label_i, title) in enumerate(
        zip(axes, y_data_list, y_label, titles)
    ):
        ax_i.plot(x_data, y_data_i)
        ax_i.grid(True)
        ax_i.set_ylabel(y_label_i)
        ax_i.set_title(title)

    if x_label is not None:
        axes[-1].set_xlabel(x_label)

    # Rotate x-axis labels for better fit
    for label in axes[-1].get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")

    fig.tight_layout()
    plt.subplots_adjust(hspace=subplot_spacing)  # Add space between subplots

    return fig


def plot_simple_multi_row_list(
    data: list[tuple[np.ndarray, np.ndarray]],
    labels: Optional[List[Optional[str]]] = None,
    y_labels: Optional[List[Optional[str]]] = None,
    x_label: Optional[str] = None,
    titles: Optional[List[Optional[str]]] = None,
    fig: Optional[Any] = None,
    axs: Optional[List[Any]] = None,
    plot_args: Optional[List[List[Any]]] = None,
    plot_kwargs: Optional[List[dict[str, Any]]] = None,
    figure_kwargs: Optional[dict[str, Any]] = None,
    legend_kwargs: Optional[dict[str, Any]] = None,
    title_kwargs: Optional[dict[str, Any]] = None,
    subplot_spacing: float = 0.15,
    *args,
    **kwargs,
) -> tuple[Any, List[Any]]:
    """
    Plot multiple (x_data, y_data) pairs on separate subplots, similar to plot_simple.

    Args:
        data (List[Tuple[np.ndarray, np.ndarray]]): List of tuples containing x and y data.
        labels (Optional[List[Optional[str]]], optional): List of labels for each plot. Defaults to None.
        y_labels (Optional[List[Optional[str]]], optional): List of Y-axis labels for each subplot. Defaults to None.
        x_label (Optional[str], optional): Common X-axis label for all subplots. Defaults to None.
        titles (Optional[List[Optional[str]]], optional): List of titles for each subplot. Defaults to None.
        fig (Optional[plt.Figure], optional): Matplotlib figure. If None, a new figure is created. Defaults to None.
        axs (Optional[List[plt.Axes]], optional): List of Matplotlib axes. If None, new axes are created. Defaults to None.
        plot_args (Optional[List[List[Any]]], optional): List of positional arguments for each plot. Defaults to None.
        plot_kwargs (Optional[List[dict[str, Any]]], optional): List of keyword arguments for each plot. Defaults to None.
        figure_kwargs (Optional[dict[str, Any]]], optional): Keyword arguments for figure creation. Defaults to None.
        legend_kwargs (Optional[dict[str, Any]]], optional): Keyword arguments for legends. Defaults to None.
        title_kwargs (Optional[dict[str, Any]]], optional): Keyword arguments for titles. Defaults to None.
        subplot_spacing (float, optional): Spacing between subplots. Defaults to 0.15.
        *args: Additional positional arguments passed to plt.plot().
        **kwargs: Additional keyword arguments passed to plt.plot().

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: The figure and list of axes of the plot.
    """

    if figure_kwargs is None:
        figure_kwargs = {
            "tight_layout": True,
            "figsize": (8, 2 * len(data)),  # Adjust height based on number of subplots
        }

    if fig is None and axs is None:
        fig, axs = plt.subplots(len(data), 1, sharex=True, **figure_kwargs)
        if len(data) == 1:
            axs = [axs]  # Ensure axs is always a list
    elif axs is None:
        fig, axs = plt.subplots(len(data), 1, sharex=True, **figure_kwargs)
        if len(data) == 1:
            axs = [axs]

    if labels is None:
        labels = [None] * len(data)
    if y_labels is None:
        y_labels = [None] * len(data)
    if titles is None:
        titles = [None] * len(data)
    if plot_args is None:
        plot_args = [[] for _ in range(len(data))]
    if plot_kwargs is None:
        plot_kwargs = [{} for _ in range(len(data))]

    for i, ((x_data, y_data), ax) in enumerate(zip(data, axs)):
        label = labels[i] if i < len(labels) else None
        y_label = y_labels[i] if i < len(y_labels) else None
        title = titles[i] if i < len(titles) else None
        args_i = plot_args[i] if i < len(plot_args) else []
        kwargs_i = plot_kwargs[i] if i < len(plot_kwargs) else {}

        # Plot using ax.plot with provided arguments
        ax.plot(x_data, y_data, *args_i, label=label, **kwargs_i)

        if y_label is not None:
            ax.set_ylabel(y_label)

        if title is not None:
            ax.set_title(title, **(title_kwargs or {}))

        if label is not None and legend_kwargs is not None:
            ax.legend(**legend_kwargs)

        ax.grid(True)

    if x_label is not None:
        axs[-1].set_xlabel(x_label)

    # Rotate x-axis labels for better fit
    for label in axs[-1].get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")

    fig.tight_layout()
    plt.subplots_adjust(hspace=subplot_spacing)  # Add space between subplots

    return fig, axs
