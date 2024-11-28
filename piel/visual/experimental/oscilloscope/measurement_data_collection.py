import piel.types
from piel.types import Unit
from piel.visual.plot.core import save
from piel.visual.plot.position import create_plot_containers
from piel.visual.plot.table import create_axes_parameters_tables_separate
from piel.visual.plot.basic import plot_simple
from piel.visual.style import secondary_color_palette
from piel.types.experimental import OscilloscopeMeasurementDataCollection
from piel.analysis.signals.time import (
    extract_rising_edges,
    resize_data_time_signal_units,
)
from typing import Optional, Literal, List, Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


def plot_oscilloscope_signals_time(
    data_collection: OscilloscopeMeasurementDataCollection,
    parameters_list: Optional[List] = None,
    xlabel: Union[str, Unit] = None,
    ylabel: Union[str, Unit] = None,
    figure_title: Optional[str] = None,
    create_parameters_tables: bool = True,
    axes_subtitle_list: Optional[List[str]] = None,
    label_per_axes: bool = False,
    label_style: Literal["label_per_axes", "label_per_figure"] = "label_per_figure",
    plot_kwargs: Optional[Dict[str, Any]] = None,
    figure_kwargs: Optional[Dict[str, Any]] = None,
    legend_kwargs: Optional[Dict[str, Any]] = None,
    rising_edges_kwargs: Optional[Dict[str, Any]] = None,
    smallest_range_s: tuple[float, float] = None,
    *args,
    **kwargs,
):
    """
    Generates a series of plots representing oscilloscope waveforms over time, where each subplot corresponds
    to a measurement in the given data collection.

    ----------
    data_collection : OscilloscopeMeasurementDataCollection
        A collection of oscilloscope measurement data, containing multiple waveforms per measurement.

    parameters_list : List[str], optional
        A list of parameter labels for the subplots. Defaults to indices if None.

    measurement_section : List[str], optional
        List of sections of the measurement for further categorization.

    xlabel : str or piel.types.Unit, optional
        The label for the x-axis. If a `piel.types.Unit` object is passed, data correction is applied based on the unit.

    ylabel : str or piel.types.Unit, optional
        The label for the y-axis. If a `piel.types.Unit` object is passed, data correction is applied based on the unit.

    figure_title : str, optional
        The title of the figure. Defaults to the name of the data collection.

    create_parameters_tables : bool, optional
        If True, creates tables of parameters for each axis. Defaults to True.

    axes_subtitle_list : List[str], optional
        A list of subtitles for each axis.

    label_per_axes : bool, optional
        If True, the x and y labels will be set individually for each axis. Defaults to False.

    label_style : Literal["label_per_axes", "label_per_figure"], default="label_per_figure"
        Determines whether labels are applied per axes or per figure.

    plot_kwargs : dict, optional
        Customization options for plotting the waveforms (e.g., line styles, colors).

    figure_kwargs : dict, optional
        Customization options for the figure (e.g., figsize, dpi).

    legend_kwargs : dict, optional
        Customization options for the legend (e.g., location, fontsize).

    rising_edges_kwargs : dict, optional
        Customization options for plotting rising edges (e.g., linestyle, color).

    *args, **kwargs :
        Additional arguments for plot customization, figure saving, or debugging.

    Returns:
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plots.

    axs : list of matplotlib.axes.Axes
        List of axes corresponding to the subplots.

    Notes:
    -----
    - The function handles multiple waveforms per measurement, plotting each waveform within its respective subplot.
    - If units are passed for `xlabel` or `ylabel`, a correction factor is applied to adjust the plotted data.
    - Parameter tables can be created for each subplot based on the `parameters_list`.
    - Rising edges can be optionally highlighted if `rising_edges_kwargs` is provided.
    """
    if parameters_list is None:
        parameters_list = []

    if plot_kwargs is None:
        plot_kwargs = {}

    if legend_kwargs is None:
        legend_kwargs = {"loc": "upper right"}

    if figure_kwargs is None:
        figure_kwargs = {}

    if isinstance(xlabel, str):
        xlabel_str = xlabel
        x_unit = piel.types.s
    elif isinstance(xlabel, Unit):
        xlabel_str = xlabel.label
        x_unit = xlabel
    else:
        xlabel_str = r"Time $s$"
        x_unit = piel.types.s

    if isinstance(ylabel, str):
        ylabel_str = ylabel
        y_unit = piel.types.V
    elif isinstance(ylabel, Unit):
        ylabel_str = ylabel.label
        y_unit = ylabel
    else:
        ylabel_str = r"Voltage $V$"
        y_unit = piel.types.V

    if figure_title is None:
        figure_title = getattr(data_collection, "name", "Oscilloscope Measurement")

    fig, axs = create_plot_containers(
        data_collection.collection,
        sharex=True,
        **figure_kwargs,
    )

    parameter_tables_list = []

    for i, osc_measurement_data in enumerate(data_collection.collection):
        if osc_measurement_data.waveform_list is None:
            logger.warning(f"No waveforms found for measurement {i}. Skipping.")
            axs[i].set_visible(False)
            continue

        ax = axs[i]
        parameter_tables_list.append(
            parameters_list[i] if parameters_list else f"Measurement {i + 1}"
        )

        for waveform in osc_measurement_data.waveform_list:
            if (waveform.time_s is None) or (waveform.data is None):
                logger.warning(
                    f"Empty waveform '{waveform.data_name}' in measurement {i}. Skipping."
                )
                continue

            # Resize waveform data based on units
            resized_waveform = resize_data_time_signal_units(
                waveform,
                time_unit=x_unit,
                data_unit=y_unit,
            )

            start_time = resized_waveform.time_s[0]
            end_time = resized_waveform.time_s[-1]
            current_range = end_time - start_time

            # Update the smallest range if the current one is smaller
            if smallest_range_s is None or current_range < smallest_range_s:
                smallest_range_s = current_range
                smallest_start = start_time
                smallest_end = end_time

            # Plot the waveform
            plot_simple(
                resized_waveform.time_s,
                resized_waveform.data,
                fig=fig,
                axs=[ax],
                label=waveform.data_name,
                plot_kwargs=plot_kwargs,
                legend_kwargs=legend_kwargs,
                figure_kwargs=figure_kwargs,
            )

            # Optionally plot rising edges
            if rising_edges_kwargs is not None:
                if not rising_edges_kwargs:
                    rising_edges_kwargs = {"linestyle": "--"}

                rising_edges = extract_rising_edges(resized_waveform)
                for edge in rising_edges:
                    plot_simple(
                        edge.time_s,
                        edge.data,
                        fig=fig,
                        axs=[ax],
                        # label=f"{waveform.data_name} Rising Edge",
                        plot_kwargs={
                            "color": secondary_color_palette[i],
                            **rising_edges_kwargs,
                        },
                        legend_kwargs=legend_kwargs,
                        figure_kwargs=figure_kwargs,
                    )

        if label_per_axes:
            ax.set_ylabel(ylabel_str)
            ax.set_xlabel(xlabel_str)
        elif label_style == "label_per_figure":
            if i == len(data_collection.collection) - 1:
                ax.set_xlabel(xlabel_str)
            ax.set_ylabel(ylabel_str)

    # Set the x-limits to the smallest range found across all waveforms
    if smallest_start is not None and smallest_end is not None:
        for ax in axs:
            if ax.get_visible():
                ax.set_xlim([smallest_start, smallest_end])
    else:
        logger.warning("No valid waveforms found to set x-limits.")

    # Create parameter tables if required
    if create_parameters_tables and parameters_list:
        if len(parameters_list) == len(data_collection.collection):
            try:
                create_axes_parameters_tables_separate(
                    fig=fig, axs=axs, parameter_tables_list=parameter_tables_list
                )
            except Exception as e:
                if kwargs.get("debug", False):
                    raise e
                else:
                    logger.error(f"Failed to create parameter tables: {e}")

    # Add subtitles to axes if provided
    if axes_subtitle_list:
        for i, subtitle in enumerate(axes_subtitle_list):
            if i < len(axs):
                axs[i].set_title(subtitle, loc="left")

    # Set the main title of the figure
    fig.suptitle(figure_title)

    # Apply label style
    if label_style == "label_per_figure":
        fig.supxlabel(xlabel_str)
        fig.supylabel(ylabel_str)

    # Save the figure
    save(fig, **kwargs)

    return fig, axs


#
# # Example Usage
# if __name__ == "__main__":
#     from piel.types.units import s, V
#     from piel.types.signal.time_data import TimeSignalData
#
#     # Create sample data
#     waveform1 = TimeSignalData(
#         time_s=[0, 1, 2, 3, 4, 5],
#         data=[0, 1, 0, 1, 0, 1],
#         data_name="Channel 1",
#         time_s_unit=s,
#         data_unit=V
#     )
#
#     waveform2 = TimeSignalData(
#         time_s=[0, 1, 2, 3, 4, 5],
#         data=[0, 0.5, 0, 0.5, 0, 0.5],
#         data_name="Channel 2",
#         time_s_unit=s,
#         data_unit=V
#     )
#
#     osc_measurement = OscilloscopeMeasurementDataCollection(
#         collection=[
#             OscilloscopeMeasurementData(
#                 measurements=None,
#                 waveform_list=[waveform1, waveform2]
#             )
#         ]
#     )
#
#     # Plot the data
#     fig, axs = plot_oscilloscope_signals_time(
#         data_collection=osc_measurement,
#         xlabel="Time (s)",
#         ylabel="Voltage (V)",
#         figure_title="Oscilloscope Waveforms",
#         plot_kwargs={"linewidth": 2},
#         rising_edges_kwargs={"linestyle": "--"},
#         debug=True
#     )
