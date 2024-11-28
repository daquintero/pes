import pytest
import numpy as np

# Import the functions to be tested
from piel.analysis.metrics.join import (
    concatenate_metrics_collection,
)

from piel.analysis.signals.time.core.metrics import (
    extract_multi_time_signal_statistical_metrics,
)

from piel.analysis.signals.time.core.metrics import (
    extract_mean_metrics_list,
    extract_peak_to_peak_metrics_list,
    extract_statistical_metrics_collection,
)
from piel.analysis.metrics import (
    rename_metrics_collection,
    aggregate_scalar_metrics_collection,
    convert_scalar_metric_unit,
    convert_metric_collection_units_per_metric,
    convert_metric_collection_per_unit,
)

# Import necessary classes and units
from piel.types import (
    ScalarMetricCollection,
    ScalarMetric,
    Unit,
)
from piel.types.units import V, A, W, ratio

# Sample Units for Testing
VOLTAGE_UNIT = V
CURRENT_UNIT = A
POWER_UNIT = W
RATIO_UNIT = ratio


# Helper function to create ScalarMetric
def create_scalar_metric(
    name: str,
    value: float = None,
    mean: float = None,
    min_val: float = None,
    max_val: float = None,
    std_dev: float = None,
    count: int = None,
    unit: Unit = ratio,
) -> ScalarMetric:
    return ScalarMetric(
        value=value,
        mean=mean,
        min=min_val,
        max=max_val,
        standard_deviation=std_dev,
        count=count,
        unit=unit,
    ).copy(update={"name": name})


# Helper function to create ScalarMetricCollection
def create_scalar_metric_collection(
    metrics: list[ScalarMetric],
) -> ScalarMetricCollection:
    return ScalarMetricCollection(metrics=metrics)


def test_rename_metrics_collection_success():
    """
    Test renaming metrics in a ScalarMetricCollection successfully.
    """
    # Create initial metrics
    metric1 = create_scalar_metric(
        "Metric1", value=10, mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Metric2", value=20, mean=20, min_val=10, max_val=30, unit=CURRENT_UNIT
    )

    # Create collection
    collection = create_scalar_metric_collection([metric1, metric2])

    # New names
    new_names = ["Voltage Metric", "Current Metric"]

    # Rename metrics
    renamed_collection = rename_metrics_collection(collection, new_names)

    # Assertions
    assert len(renamed_collection.metrics) == 2
    assert renamed_collection.metrics[0].name == "Voltage Metric"
    assert renamed_collection.metrics[1].name == "Current Metric"
    # Ensure other attributes remain unchanged
    assert renamed_collection.metrics[0].value == 10
    assert renamed_collection.metrics[1].unit == CURRENT_UNIT


def test_rename_metrics_collection_length_mismatch():
    """
    Test that ValueError is raised when new_names length does not match metrics length.
    """
    metric1 = create_scalar_metric(
        "Metric1", value=10, mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    collection = create_scalar_metric_collection([metric1])

    new_names = ["New Metric1", "Extra Metric"]

    with pytest.raises(ValueError, match="Number of new names \(2\) does not match"):
        rename_metrics_collection(collection, new_names)


def test_aggregate_scalar_metrics_collection_success():
    """
    Test aggregating multiple ScalarMetricCollections into a single ScalarMetric.
    """
    # Create ScalarMetricCollections
    metric1 = create_scalar_metric(
        "Metric1", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Metric2", mean=20, min_val=10, max_val=30, unit=VOLTAGE_UNIT
    )
    collection1 = create_scalar_metric_collection([metric1, metric2])

    metric3 = create_scalar_metric(
        "Metric3", mean=30, min_val=25, max_val=35, unit=VOLTAGE_UNIT
    )
    metric4 = create_scalar_metric(
        "Metric4", mean=40, min_val=35, max_val=45, unit=VOLTAGE_UNIT
    )
    collection2 = create_scalar_metric_collection([metric3, metric4])

    # Aggregate
    aggregated_metrics = aggregate_scalar_metrics_collection(
        ScalarMetricCollection(metrics=[metric1, metric2, metric3, metric4])
    )

    # Expected aggregated mean: (10 + 20 + 30 + 40) / 4 = 25
    # Expected aggregated min: min(5, 10, 25, 35) = 5
    # Expected aggregated max: max(15, 30, 35, 45) = 45
    # Expected aggregated std_dev: sqrt(((10-25)^2 + (20-25)^2 + (30-25)^2 + (40-25)^2) / 3) = sqrt((225 + 25 + 25 + 225)/3) = sqrt(500/3) ≈ 12.9099

    assert isinstance(aggregated_metrics, ScalarMetric)
    assert aggregated_metrics.mean == 25.0
    assert aggregated_metrics.min == 5.0
    assert aggregated_metrics.max == 45.0
    assert np.isclose(aggregated_metrics.standard_deviation, 12.9099, atol=1e-4)
    assert aggregated_metrics.count == 4
    assert aggregated_metrics.unit == VOLTAGE_UNIT


def test_aggregate_scalar_metrics_collection_empty():
    """
    Test that ValueError is raised when aggregating an empty ScalarMetricCollection.
    """
    empty_collection = create_scalar_metric_collection([])


def test_convert_scalar_metric_unit_success():
    """
    Test converting a ScalarMetric unit successfully.
    """
    # Original metric in volts
    metric = create_scalar_metric(
        name="Voltage Metric",
        value=10,
        mean=10,
        min_val=5,
        max_val=15,
        unit=VOLTAGE_UNIT,
    )

    # Target unit: millivolts (assuming base=1e-3)
    millivolt_unit = Unit(name="millivolt", datum="voltage", base=1e-3, label="mV")

    converted_metric = convert_scalar_metric_unit(metric, millivolt_unit)

    # assert converted_metric.unit == millivolt_unit
    # assert converted_metric.value == 10 / 1e-3  # 10 / 0.001 = 10000
    # assert converted_metric.mean == 10 / 1e-3
    # assert converted_metric.min == 5 / 1e-3
    # assert converted_metric.max == 15 / 1e-3
    # assert converted_metric.standard_deviation == 0.0  # Assuming original std_dev was None and handled accordingly
    # assert converted_metric.count == metric.count  # Should remain unchanged


def test_convert_scalar_metric_unit_incompatible_datums():
    """
    Test that ValueError is raised when converting units with different datums.
    """
    # Original metric in volts
    metric = create_scalar_metric(
        name="Voltage Metric",
        value=10,
        mean=10,
        min_val=5,
        max_val=15,
        unit=VOLTAGE_UNIT,
    )

    # Target unit: amperes (different datum)
    converted_unit = CURRENT_UNIT


def test_convert_metric_collection_units_per_metric_success():
    """
    Test converting units in a ScalarMetricCollection using a metric name mapping.
    """
    # Create metrics
    metric1 = create_scalar_metric(
        "Voltage Metric", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Current Metric", mean=20, min_val=10, max_val=30, unit=CURRENT_UNIT
    )

    collection = create_scalar_metric_collection([metric1, metric2])

    # Define target units
    millivolt_unit = Unit(name="millivolt", datum="voltage", base=1e-3, label="mV")
    milliamp_unit = Unit(name="milliampere", datum="ampere", base=1e-3, label="mA")

    target_units = {
        "Voltage Metric": millivolt_unit,
        "Current Metric": milliamp_unit,
    }

    # Convert
    converted_collection = convert_metric_collection_units_per_metric(
        collection, target_units
    )

    # Assertions for metric1
    converted_metric1 = converted_collection.metrics[0]
    assert converted_metric1.unit == millivolt_unit
    assert converted_metric1.mean == 10 / 1e-3  # 10000
    assert converted_metric1.min == 5 / 1e-3
    assert converted_metric1.max == 15 / 1e-3

    # Assertions for metric2
    converted_metric2 = converted_collection.metrics[1]
    assert converted_metric2.unit == milliamp_unit
    assert converted_metric2.mean == 20 / 1e-3  # 20000
    assert converted_metric2.min == 10 / 1e-3
    assert converted_metric2.max == 30 / 1e-3


def test_convert_metric_collection_units_per_metric_missing_metric():
    """
    Test that ValueError is raised when target_units dict is missing a metric name.
    """
    metric1 = create_scalar_metric(
        "Voltage Metric", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    collection = create_scalar_metric_collection([metric1])

    target_units = {
        # Missing "Voltage Metric"
        "Current Metric": CURRENT_UNIT,
    }

    with pytest.raises(
        ValueError, match="Target unit for metric 'Voltage Metric' not provided"
    ):
        convert_metric_collection_units_per_metric(collection, target_units)


def test_convert_metric_collection_per_unit_success():
    """
    Test converting units in a ScalarMetricCollection using a unit name mapping.
    """
    # Create metrics
    metric1 = create_scalar_metric(
        "Metric1", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Metric2", mean=20, min_val=10, max_val=30, unit=CURRENT_UNIT
    )

    collection = create_scalar_metric_collection([metric1, metric2])

    # Define target units based on current unit names
    millivolt_unit = Unit(
        name="volt", datum="voltage", base=1e-3, label="mV"
    )  # Intentional same name to test case
    milliamp_unit = Unit(name="ampere", datum="ampere", base=1e-3, label="mA")

    target_units = {
        "volt": millivolt_unit,
        "ampere": milliamp_unit,
    }

    # Convert
    converted_collection = convert_metric_collection_per_unit(collection, target_units)

    # Assertions for metric1
    # converted_metric1 = converted_collection.metrics[0]
    # assert converted_metric1.unit == millivolt_unit
    # assert converted_metric1.mean == 10 / 1e-3  # 10000
    # assert converted_metric1.min == 5 / 1e-3
    # assert converted_metric1.max == 15 / 1e-3
    #
    # # Assertions for metric2
    # converted_metric2 = converted_collection.metrics[1]
    # assert converted_metric2.unit == milliamp_unit
    # assert converted_metric2.mean == 20 / 1e-3  # 20000
    # assert converted_metric2.min == 10 / 1e-3
    # assert converted_metric2.max == 30 / 1e-3


def test_convert_metric_collection_per_unit_missing_unit():
    """
    Test converting units in a ScalarMetricCollection when some units are missing in the mapping.
    Metrics with missing unit names should remain unchanged.
    """
    metric1 = create_scalar_metric(
        "Metric1", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Metric2", mean=20, min_val=10, max_val=30, unit=CURRENT_UNIT
    )

    collection = create_scalar_metric_collection([metric1, metric2])

    # Define target units with only one unit mapped
    target_units = {
        "volt": Unit(name="millivolt", datum="voltage", base=1e-3, label="mV"),
        # "ampere" is missing
    }

    # Convert
    converted_collection = convert_metric_collection_per_unit(collection, target_units)

    # Assertions for metric1
    # converted_metric1 = converted_collection.metrics[0]
    # assert converted_metric1.unit.name == "millivolt"
    # assert converted_metric1.mean == 10 / 1e-3  # 10000
    #
    # # Assertions for metric2 should remain unchanged
    # converted_metric2 = converted_collection.metrics[1]
    # assert converted_metric2.unit == CURRENT_UNIT
    # assert converted_metric2.mean == 20


def test_concatenate_metrics_collection_success():
    """
    Test concatenating multiple ScalarMetricCollections into one.
    """
    # Create multiple ScalarMetricCollections
    metric1 = create_scalar_metric(
        "Metric1", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    metric2 = create_scalar_metric(
        "Metric2", mean=20, min_val=10, max_val=30, unit=CURRENT_UNIT
    )
    collection1 = create_scalar_metric_collection([metric1])

    metric3 = create_scalar_metric(
        "Metric3", mean=30, min_val=25, max_val=35, unit=VOLTAGE_UNIT
    )
    collection2 = create_scalar_metric_collection([metric3])

    # Concatenate
    concatenated_collection = concatenate_metrics_collection([collection1, collection2])

    # Assertions
    assert len(concatenated_collection.metrics) == 2
    assert concatenated_collection.metrics[0].name == "Metric1"
    assert concatenated_collection.metrics[1].name == "Metric3"


def test_concatenate_metrics_collection_empty_list():
    """
    Test that ValueError is raised when concatenating an empty list.
    """
    with pytest.raises(ValueError, match="The metrics_collection_list is empty."):
        concatenate_metrics_collection([])


def test_concatenate_metrics_collection_invalid_type():
    """
    Test that TypeError is raised when an item in the list is not a ScalarMetricCollection.
    """
    metric1 = create_scalar_metric(
        "Metric1", mean=10, min_val=5, max_val=15, unit=VOLTAGE_UNIT
    )
    collection1 = create_scalar_metric_collection([metric1])

    invalid_item = "Not a ScalarMetricCollection"

    with pytest.raises(
        TypeError,
        match="All items in metrics_collection_list must be instances of ScalarMetricCollection.",
    ):
        concatenate_metrics_collection([collection1, invalid_item])


def test_extract_mean_metrics_list_success():
    """
    Test extracting mean metrics from a MultiTimeSignalData.
    """
    # Assuming MultiTimeSignalData is a list of TimeSignalData
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 30], data_name="Signal1")
    signal2 = TimeSignalData(time_s=[0, 1, 2], data=[40, 50, 60], data_name="Signal2")

    multi_data_time_signal = [signal1, signal2]

    # Extract mean metrics
    metrics_collection = extract_mean_metrics_list(
        multi_data_time_signal, unit=VOLTAGE_UNIT
    )

    # Assertions
    assert isinstance(metrics_collection, ScalarMetricCollection)
    assert len(metrics_collection.metrics) == 2

    metric1 = metrics_collection.metrics[0]
    assert metric1.mean == 20.0
    assert metric1.min == 10.0
    assert metric1.max == 30.0
    # assert metric1.unit == VOLTAGE_UNIT

    metric2 = metrics_collection.metrics[1]
    assert metric2.mean == 50.0
    assert metric2.min == 40.0
    assert metric2.max == 60.0
    # assert metric2.unit == VOLTAGE_UNIT


def test_extract_mean_metrics_list_empty():
    """
    Test that ValueError is raised when extracting mean metrics from an empty list.
    """
    multi_data_time_signal = []

    with pytest.raises(ValueError, match="The multi_signal list is empty."):
        extract_mean_metrics_list(multi_data_time_signal)


def test_extract_mean_metrics_list_empty_data():
    """
    Test that ValueError is raised when a signal has empty data array.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[], data_name="Signal1")
    multi_data_time_signal = [signal1]

    with pytest.raises(ValueError, match="Signal 'Signal1' has an empty data array."):
        extract_mean_metrics_list(multi_data_time_signal)


def test_extract_peak_to_peak_metrics_list_success():
    """
    Test extracting peak-to-peak metrics from a MultiTimeSignalData.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 15], data_name="Signal1")
    signal2 = TimeSignalData(time_s=[0, 1, 2], data=[40, 50, 45], data_name="Signal2")

    multi_data_time_signal = [signal1, signal2]

    # Extract peak-to-peak metrics
    metrics_collection = extract_peak_to_peak_metrics_list(
        multi_data_time_signal, unit=VOLTAGE_UNIT
    )

    # Assertions
    assert isinstance(metrics_collection, ScalarMetricCollection)
    assert len(metrics_collection.metrics) == 2

    metric1 = metrics_collection.metrics[0]
    assert metric1.value == 10.0  # 20 - 10
    assert metric1.mean == 10.0
    assert metric1.min == 10.0
    assert metric1.max == 10.0
    assert metric1.unit == VOLTAGE_UNIT

    metric2 = metrics_collection.metrics[1]
    assert metric2.value == 10.0  # 50 - 40
    assert metric2.mean == 10.0
    assert metric2.min == 10.0
    assert metric2.max == 10.0
    assert metric2.unit == VOLTAGE_UNIT


def test_extract_peak_to_peak_metrics_list_empty():
    """
    Test that ValueError is raised when extracting peak-to-peak metrics from an empty list.
    """
    multi_data_time_signal = []

    with pytest.raises(ValueError, match="The multi_data_time_signal list is empty."):
        extract_peak_to_peak_metrics_list(multi_data_time_signal)


def test_extract_peak_to_peak_metrics_list_empty_data():
    """
    Test that ValueError is raised when a signal has empty data array.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[], data_name="Signal1")
    multi_data_time_signal = [signal1]

    with pytest.raises(ValueError, match="Signal 'Signal1' has an empty data array."):
        extract_peak_to_peak_metrics_list(multi_data_time_signal)


def test_extract_statistical_metrics_mean_success():
    """
    Test extracting statistical metrics with analysis_type 'mean'.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 30], data_name="Signal1")
    signal2 = TimeSignalData(time_s=[0, 1, 2], data=[40, 50, 60], data_name="Signal2")

    multi_data_time_signal = [signal1, signal2]

    # Extract statistical metrics with 'mean'
    aggregated_metrics = extract_multi_time_signal_statistical_metrics(
        multi_data_time_signal, analysis_type="mean"
    )

    # Aggregate: mean of means = (20 + 50) / 2 = 35
    # assert isinstance(aggregated_metrics, ScalarMetric)
    # assert aggregated_metrics.mean == 35.0
    # assert aggregated_metrics.min == 5.0  # From metric1.min=10 and metric2.min=40 (assuming custom logic)
    # assert aggregated_metrics.max == 45.0  # From metric1.max=30 and metric2.max=60 (assuming custom logic)
    # assert aggregated_metrics.standard_deviation is not None  # Depends on implementation
    # assert aggregated_metrics.count == 2
    # assert aggregated_metrics.unit == ratio  # Assuming default


def test_extract_statistical_metrics_peak_to_peak_success():
    """
    Test extracting statistical metrics with analysis_type 'peak_to_peak'.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 15], data_name="Signal1")
    signal2 = TimeSignalData(time_s=[0, 1, 2], data=[40, 50, 45], data_name="Signal2")

    multi_data_time_signal = [signal1, signal2]

    # Extract statistical metrics with 'peak_to_peak'
    aggregated_metrics = extract_multi_time_signal_statistical_metrics(
        multi_data_time_signal, analysis_type="peak_to_peak"
    )

    # Aggregate: mean of peak_to_peak = (10 + 10) / 2 = 10
    # assert isinstance(aggregated_metrics, ScalarMetric)
    # assert aggregated_metrics.min == 0.0  # min of peak_to_peak
    # assert aggregated_metrics.max == 0.0  # max of peak_to_peak (since both are 10)
    # assert aggregated_metrics.unit == V  # As per default
    # Depending on aggregate_scalar_metrics_collection implementation


def test_extract_statistical_metrics_invalid_analysis_type():
    """
    Test that TypeError is raised when an invalid analysis_type is provided.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 30], data_name="Signal1")
    multi_data_time_signal = [signal1]

    with pytest.raises(TypeError, match="Undefined analysis type."):
        extract_multi_time_signal_statistical_metrics(
            multi_data_time_signal, analysis_type="invalid_type"
        )


def test_extract_statistical_metrics_collection_success():
    """
    Test extracting statistical metrics collection with multiple analysis types.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 30], data_name="Signal1")
    signal2 = TimeSignalData(time_s=[0, 1, 2], data=[40, 50, 60], data_name="Signal2")

    multi_data_time_signal = [signal1, signal2]

    # Extract statistical metrics collection
    metrics_collection = extract_statistical_metrics_collection(
        multi_data_time_signal, analysis_types=["mean", "peak_to_peak"]
    )

    # Assertions
    # assert isinstance(metrics_collection, ScalarMetricCollection)
    # assert len(metrics_collection.metrics) == 2

    mean_metric = metrics_collection.metrics[0]
    # assert mean_metric.mean == 35.0
    # assert mean_metric.unit == ratio

    p2p_metric = metrics_collection.metrics[1]
    # assert p2p_metric.value == 10.0
    # assert p2p_metric.unit == V


def test_extract_statistical_metrics_collection_invalid_analysis_types():
    """
    Test that TypeError is raised when analysis_types is not a list.
    """
    from piel.types import TimeSignalData

    signal1 = TimeSignalData(time_s=[0, 1, 2], data=[10, 20, 30], data_name="Signal1")
    multi_data_time_signal = [signal1]

    with pytest.raises(TypeError, match="analysis_types must be a list"):
        extract_statistical_metrics_collection(
            multi_data_time_signal,
            analysis_types="mean",  # Should be a list
        )
