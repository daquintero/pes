from .....types import Instance
from ...experiment import Experiment
from .generic import MeasurementDataCollectionTypes


class ExperimentData(Instance):
    """
    This is a definition of a collection of experimental data.
    """

    experiment: Experiment
    data: MeasurementDataCollectionTypes

    # TODO add validators to make sure data and experimental parameters are the same size
    # TODO add validators for data type matches experiment type
