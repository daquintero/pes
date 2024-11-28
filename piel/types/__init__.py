"""
Top Level Types Declaration, all should be imported here.

These types are intended to be pure static types. They can only contain parameter definitions of the data types,
add data type validators, and the only functions that can be added in these types is overwriting the base class
base hidden methods. No other methods can be added here. This is because these classes are intended to be pure data
types which are operated upon purely. If we begin adding custom methods on the type definitions, not only do they become bloated,
but functional composition complexity is increased and the "static" data types become a hell to manage.
"""

from piel.types.analogue import AnalogueModule, AnalogModule

from piel.types.core import (
    PathTypes,
    PielBaseModel,
    NumericalTypes,
    ArrayTypes,
    TupleIntType,
    TupleFloatType,
    TupleNumericalType,
    PackageArrayType,
    ModuleType,
)
from piel.types.connectivity.core import Instance
from piel.types.constants import c
from piel.types.connectivity.abstract import Connection, Component, Port
from piel.types.connectivity.generic import (
    ConnectionTypes,
    PortTypes,
    ComponentTypes,
    ComponentCollection,
)
from piel.types.connectivity.physical import (
    PhysicalComponent,
    PhysicalConnection,
    PhysicalPort,
)
from piel.types.connectivity.metrics import ComponentMetrics
from piel.types.connectivity.timing import (
    TimeMetric,
    DispersiveTimeMetrics,
    TimeMetricsTypes,
    ZeroTimeMetrics,
)

from piel.types.digital import (
    DigitalLogicModule,
    AbstractBitsType,
    BitsType,
    BitsList,
    DigitalRunID,
    HDLSimulator,
    HDLTopLevelLanguage,
    LogicSignalsList,
    LogicImplementationType,
    TruthTable,
    TruthTableLogicType,
)
from piel.types.digital_electro_optic import BitPhaseMap

from piel.types.environment import Environment
from piel.types.experimental import *  # NOQA: F403

from piel.types.electrical.cables import (
    CoaxialCableGeometryType,
    CoaxialCableHeatTransferType,
    CoaxialCableMaterialSpecificationType,
    DCCableGeometryType,
    DCCableHeatTransferType,
    DCCableMaterialSpecificationType,
    DCCable,
    CoaxialCable,
)

from piel.types.electrical.pcb import PCB

from piel.types.electrical.rf_calibration import Short, Open, Load, Through

from piel.types.electrical.rf_passives import (
    PowerSplitter,
    BiasTee,
)

from piel.types.electro_optic.transition import (
    FockStatePhaseTransition,
    OpticalStateTransitionCollection,
    PhaseMapType,
    PhaseTransitionTypes,
    SwitchFunctionParameter,
    SParameterCollection,
)

from piel.types.electro_optic.modulator import (
    ElectroOpticModulatorMetrics,
    ElectroOpticModulator,
)

from piel.types.electro_optic.laser import PulsedLaserMetrics, PulsedLaser

from piel.types.electronic.core import (
    ElectronicCircuit,
    ElectronicChip,
    ElectronicCircuitComponent,
)
from piel.types.electronic.amplifier import RFTwoPortAmplifier
from piel.types.electronic.generic import RFAmplifierCollection, RFAmplifierTypes
from piel.types.electronic.hva import PowerAmplifierMetrics, PowerAmplifier
from piel.types.electronic.lna import LNAMetrics, LowNoiseTwoPortAmplifier

from piel.types.file_system import ProjectType
from piel.types.integration import CircuitComponent
from piel.types.materials import (
    MaterialReferenceType,
    MaterialReferencesTypes,
    MaterialSpecificationType,
)

from piel.types.metrics import ScalarMetric, ScalarMetricCollection

from piel.types.photonic import (
    PhotonicCircuitComponent,
    OpticalTransmissionCircuit,
    RecursiveNetlist,
    SParameterMatrixTuple,
)

from piel.types.signal.core import ElectricalSignalDomains, QuantityTypesDC

from piel.types.signal.dc_data import (
    SignalDCCollection,
    SignalTraceDC,
    SignalDC,
)

from piel.types.signal.frequency.core import Phasor

from piel.types.signal.frequency.generic import (
    PhasorTypes,
)

from piel.types.signal.frequency.transmission import (
    PathTransmission,
    NetworkTransmission,
    FrequencyTransmissionModel,
    FrequencyTransmissionList,
)

from piel.types.signal.frequency.metrics import (
    FrequencyMetricCollection,
    FrequencyMetric,
)

# from piel.types.signal.frequency.sax_core import (
#     Array,
#     Complex,
#     ComplexArrayND,
#     ComplexArray1D,
#     FloatArray1D,
#     FloatArrayND,
#     IntArray1D,
#     IntArrayND,
#     Int,
#     ConnectionTypes,
#     PortCombination,
#     SDict,
#     SType,
#     SCoo,
#     SDense,
# )  # For pure-sax compatibility.


from piel.types.signal.electro_optic import (
    ElectroOpticDCPathTransmission,
    ElectroOpticDCNetworkTransmission,
)

from piel.types.signal.time_data import (
    TimeSignalData,
    DataTimeSignalData,
    EdgeTransitionAnalysisTypes,
    MultiTimeSignalData,
    MultiDataTimeSignal,
    MultiDataTimeSignalCollectionTypes,
    MultiDataTimeSignalAnalysisTypes,
    DataTimeSignalAnalysisTypes,
)


from piel.types.signal.time_sources import (
    ExponentialSource,
    PulseSource,
    PiecewiseLinearSource,
    SineSource,
    SignalTimeSources,
)

from piel.types.symbolic import SymbolicValue

from piel.types.reference import Reference

from piel.types.quantity import Quantity

# Always last

from piel.types.units import (
    Unit,
    BaseSIUnitNameList,
    A,
    dB,
    dBm,
    degree,
    GHz,
    Hz,
    nm,
    ns,
    m,
    MHz,
    mm2,
    mW,
    ohm,
    ps,
    ratio,
    s,
    us,
    W,
    V,
)
