from typing import Literal
from piel.types.core import PielBaseModel, ArrayTypes
from piel.types.units import Unit, s, V


class TimeSignalData(PielBaseModel):
    """
    Standard definition for a relationship between a relevant files signal and a time reference array.
    Sources could be both measurement and simulation.
    """

    time_s: ArrayTypes = []
    data: ArrayTypes = []
    data_name: str = ""
    time_s_unit: Unit = s
    data_unit: Unit = V


DataTimeSignalData = TimeSignalData  # Legacy, to be removed
MultiTimeSignalData = list[TimeSignalData]
MultiDataTimeSignal = MultiTimeSignalData  # Legacy, to be removed

"""
Collection of DataTimeSignals that can be used to analyse a set of signals together in a particular files flow.
"""
MultiDataTimeSignalCollectionTypes = ["equivalent", "different"]

EdgeTransitionAnalysisTypes = Literal["mean", "peak_to_peak", "rise_time"]
MultiDataTimeSignalAnalysisTypes = Literal["delay"]

DataTimeSignalAnalysisTypes = (
    EdgeTransitionAnalysisTypes | MultiDataTimeSignalAnalysisTypes
)
