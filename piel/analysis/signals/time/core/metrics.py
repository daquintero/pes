import numpy as np
from piel.types import (
    MultiTimeSignalData,
    ScalarMetric,
    EdgeTransitionAnalysisTypes,
    ScalarMetricCollection,
)
from piel.types.units import V
from piel.analysis.metrics import aggregate_scalar_metrics_collection


def extract_mean_metrics_list(
    multi_data_time_signal: MultiTimeSignalData, **kwargs
) -> ScalarMetricCollection:
    """
    Extracts scalar metrics from a collection of rising edge signals. Standard deviation is not calculated as this just
    computes individual metrics list.

    Args:
        multi_data_time_signal (List[TimeSignalData]): A list of rising edge signals.

    Returns:
        ScalarMetricCollection: A collection of ScalarMetric instances containing the extracted metrics.
    """
    if not multi_data_time_signal:
        raise ValueError("The multi_signal list is empty.")

    if kwargs.get("unit") is None:
        kwargs["unit"] = V

    metrics_list = []

    for signal in multi_data_time_signal:
        if not signal.data:
            raise ValueError(f"Signal '{signal.data_name}' has an empty data array.")

        data_array = np.array(signal.data)

        mean_val = float(np.mean(data_array))
        min_val = float(np.min(data_array))
        max_val = float(np.max(data_array))
        std_dev = None
        count = None

        # Assuming 'value' is the mean; adjust if different meaning is intended
        scalar_metric = ScalarMetric(
            value=mean_val,
            mean=mean_val,
            min=min_val,
            max=max_val,
            standard_deviation=std_dev,
            count=count,
        )

        metrics_list.append(scalar_metric)

    return ScalarMetricCollection(metrics=metrics_list, **kwargs)


def extract_peak_to_peak_metrics_list(
    multi_data_time_signal: MultiTimeSignalData,
    metric_kwargs_list: list[dict] = None,
    **kwargs,
) -> ScalarMetricCollection:
    """
    Extracts peak-to-peak metrics from a collection of signals. The peak-to-peak value is defined as the
    difference between the maximum and minimum values of the signal.

    Args:
        multi_data_time_signal (MultiTimeSignalData): A collection of time signals to analyze.

    Returns:
        ScalarMetricCollection: A collection of ScalarMetric instances containing the peak-to-peak values
                             for each signal.

    Raises:
        ValueError: If the input list is empty or any signal has an empty data array.
    """
    if not multi_data_time_signal:
        raise ValueError("The multi_data_time_signal list is empty.")

    if metric_kwargs_list is None:
        metric_kwargs_list = [dict().copy() for _ in range(len(multi_data_time_signal))]

    if kwargs.get("unit") is None:
        kwargs["unit"] = V

    metrics_list = []

    i = 0
    for signal in multi_data_time_signal:
        if not signal.data:
            raise ValueError(f"Signal '{signal.data_name}' has an empty data array.")

        data_array = np.array(signal.data)

        min_val = float(np.min(data_array))
        max_val = float(np.max(data_array))
        peak_to_peak = max_val - min_val

        scalar_metric = ScalarMetric(
            value=peak_to_peak,  # Using peak-to-peak as the primary value
            mean=peak_to_peak,  # Mean is not applicable for peak-to-peak
            min=peak_to_peak,  # Min is already represented in peak-to-peak
            max=peak_to_peak,  # Max is already represented in peak-to-peak
            standard_deviation=None,  # Not applicable
            count=None,  # Not applicable
            unit=kwargs.get("unit"),
            **metric_kwargs_list[i],
        )

        metrics_list.append(scalar_metric)
        i += 1

    return ScalarMetricCollection(metrics=metrics_list, **kwargs)


def extract_multi_time_signal_statistical_metrics(
    multi_data_time_signal: MultiTimeSignalData,
    analysis_type: EdgeTransitionAnalysisTypes = "peak_to_peak",
    **kwargs,
) -> ScalarMetric:
    """
    Extracts scalar metrics from a collection of rising edge signals.

    Args:
        multi_data_time_signal (List[TimeSignalData]): A list of rising edge signals.
        analysis_type (piel.types.EdgeTransitionAnalysisTypes): The type of analysis to perform.

    Returns:
        ScalarMetric: Aggregated ScalarMetrics instance containing the extracted metrics.

    """
    if analysis_type == "mean":
        metrics_list = extract_mean_metrics_list(multi_data_time_signal, **kwargs)
    elif analysis_type == "peak_to_peak":
        metrics_list = extract_peak_to_peak_metrics_list(
            multi_data_time_signal, **kwargs
        )
    else:
        raise TypeError(
            f"Undefined analysis type. Current options are: {str(EdgeTransitionAnalysisTypes)}. Feel free to contribute to this."
        )
    aggregate_metrics = aggregate_scalar_metrics_collection(metrics_list)
    return aggregate_metrics


def extract_statistical_metrics_collection(
    multi_data_time_signal: MultiTimeSignalData,
    analysis_types: list[EdgeTransitionAnalysisTypes],
    **kwargs,
) -> ScalarMetricCollection:
    """
    Extracts a collection of scalar metrics from a collection of rising edge signals based on multiple analysis types.

    Args:
        multi_data_time_signal (MultiTimeSignalData): A collection of rising edge signals.
        analysis_types (list[EdgeTransitionAnalysisTypes], optional): The types of analyses to perform. Defaults to ["peak_to_peak"].

    Returns:
        ScalarMetricCollection: A collection of aggregated ScalarMetric instances for each analysis type.
    """
    if not isinstance(analysis_types, list):
        raise TypeError(
            f"analysis_types must be a list of EdgeTransitionAnalysisTypes: {EdgeTransitionAnalysisTypes}."
        )

    metrics_list = list()

    for analysis in analysis_types:
        aggregated_metrics = extract_multi_time_signal_statistical_metrics(
            multi_data_time_signal, analysis_type=analysis
        )
        metrics_list.append(aggregated_metrics)

    return ScalarMetricCollection(metrics=metrics_list, **kwargs)
