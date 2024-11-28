from piel.types.experimental import (
    PropagationDelayMeasurementData,
    PropagationDelayMeasurementDataCollection,
    MeasurementData,
    MeasurementDataCollection,
)
from piel.types import (
    TimeSignalData,
    ScalarMetricCollection,
)


# Test PropagationDelayMeasurementData
def test_propagation_delay_measurement_data_initialization():
    signal_metrics = ScalarMetricCollection()
    dut_waveform = TimeSignalData()
    reference_waveform = TimeSignalData()

    measurement_data = PropagationDelayMeasurementData(
        measurements=signal_metrics,
        dut_waveform=dut_waveform,
        reference_waveform=reference_waveform,
    )

    assert isinstance(measurement_data, MeasurementData)
    assert measurement_data.type == "PropagationDelayMeasurementData"
    assert measurement_data.measurements == signal_metrics
    assert measurement_data.dut_waveform == dut_waveform
    assert measurement_data.reference_waveform == reference_waveform


def test_propagation_delay_measurement_data_default_initialization():
    measurement_data = PropagationDelayMeasurementData()

    assert isinstance(measurement_data, MeasurementData)
    assert measurement_data.type == "PropagationDelayMeasurementData"
    assert measurement_data.measurements is None
    assert measurement_data.dut_waveform is None
    assert measurement_data.reference_waveform is None


# Test PropagationDelayMeasurementDataCollection
def test_propagation_delay_measurement_data_collection_initialization():
    data_1 = PropagationDelayMeasurementData()
    data_2 = PropagationDelayMeasurementData()

    data_collection = PropagationDelayMeasurementDataCollection(
        collection=[data_1, data_2]
    )

    assert isinstance(data_collection, MeasurementDataCollection)
    assert data_collection.type == "PropagationDelayMeasurementDataCollection"
    assert data_collection.collection == [data_1, data_2]


def test_propagation_delay_measurement_data_collection_default_initialization():
    data_collection = PropagationDelayMeasurementDataCollection()

    assert isinstance(data_collection, MeasurementDataCollection)
    assert data_collection.type == "PropagationDelayMeasurementDataCollection"
    assert data_collection.collection == []


# Add more tests as needed for additional methods, edge cases, and behaviors.
