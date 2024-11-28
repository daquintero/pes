from .core import MeasurementData, MeasurementDataCollection
from piel.types.signal.time_data import MultiTimeSignalData
from piel.types.metrics import ScalarMetricCollection


class OscilloscopeMeasurementData(MeasurementData):
    """
    Standard definition for a collection of files that are part of a generic oscilloscope measurement

    The collection includes a list of waveform files, and a measurements file.

    Attributes:
        measurements (Optional[SignalMetricsMeasurementCollection]): The collection of signal measurements.
        waveform_list (MultiTimeSignalData): The collection of waveforms.
    """

    type: str = "OscilloscopeMeasurementData"
    measurements: ScalarMetricCollection | None = None
    waveform_list: MultiTimeSignalData = []


class OscilloscopeMeasurementDataCollection(MeasurementDataCollection):
    type: str = "OscilloscopeMeasurementDataCollection"
    collection: list[OscilloscopeMeasurementData] = []
