from typing import List, Optional

from piel.types import TimeSignalData, ScalarMetricCollection
from piel.analysis.signals.time.core.split import extract_pulses_from_signal
from piel.analysis.signals.time.core.metrics import extract_peak_to_peak_metrics_list


def extract_peak_to_peak_metrics_after_split_pulses(
    full_signal: TimeSignalData,
    pre_pulse_time_s: float = 1e-9,
    post_pulse_time_s: float = 1e-9,
    noise_std_multiplier: float = 3.0,
    min_pulse_height: Optional[float] = None,
    min_pulse_distance_s: Optional[float] = None,
    data_time_signal_kwargs: Optional[dict] = None,
    metrics_kwargs: Optional[dict] = None,
) -> ScalarMetricCollection:
    """
    Extracts pulses from the full signal and computes peak-to-peak metrics.

    Parameters:
    - full_signal (TimeSignalData): The complete time signal data to be analyzed.
    - pre_pulse_time_s (float): Time in seconds before the pulse to include.
    - post_pulse_time_s (float): Time in seconds after the pulse to include.
    - noise_std_multiplier (float): Multiplier for noise standard deviation to detect pulses.
    - min_pulse_height (Optional[float]): Minimum height of a pulse to be considered.
    - min_pulse_distance_s (Optional[float]): Minimum distance in seconds between pulses.
    - data_time_signal_kwargs (Optional[dict]): Additional keyword arguments for pulse extraction.
    - metrics_kwargs (Optional[dict]): Additional keyword arguments for metric extraction.

    Returns:
    - ScalarMetricCollection: Collection of extracted scalar metrics.
    """

    try:
        # Extract pulses from the full signal
        pulses: List[TimeSignalData] = extract_pulses_from_signal(
            full_data=full_signal,
            pre_pulse_time_s=pre_pulse_time_s,
            post_pulse_time_s=post_pulse_time_s,
            noise_std_multiplier=noise_std_multiplier,
            min_pulse_height=min_pulse_height,
            min_pulse_distance_s=min_pulse_distance_s,
            data_time_signal_kwargs=data_time_signal_kwargs,
        )
        # print(len(pulses))

        # Extract peak-to-peak metrics from the pulses
        metrics: ScalarMetricCollection = extract_peak_to_peak_metrics_list(
            multi_data_time_signal=pulses, **(metrics_kwargs or {})
        )
    except Exception as e:
        print(e)
        metrics = ScalarMetricCollection()

    return metrics
