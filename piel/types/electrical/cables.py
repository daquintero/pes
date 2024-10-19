from typing import Optional, Union
from piel.types.quantity import Quantity
from piel.types.materials import MaterialReferenceType
from piel.types.radio_frequency import RFPhysicalComponent
from ..connectivity.physical import PhysicalComponent


# TODO This shouldn't be a quantity
class CoaxialCableGeometryType(Quantity):
    core_cross_sectional_area_m2: float | None = 0
    """
    The cross-sectional area of the core in meters squared.
    """

    length_m: float = 0
    """
    The length of the cable in meters.
    """

    sheath_cross_sectional_area_m2: float | None = 0
    """
    The cross-sectional area of the sheath in meters squared.
    """

    total_cross_sectional_area_m2: float | None = 0
    """
    The total cross-sectional area of the cable in meters squared.
    """


class CoaxialCableHeatTransferType(Quantity):
    """
    All units are in watts.
    """

    core: float | None = 0
    """
    The computed heat transfer in watts for the core of the cable.
    """

    sheath: float | None = 0
    """
    The computed heat transfer in watts for the sheath of the cable.
    """

    dielectric: float | None = 0
    """
    The computed heat transfer in watts for the dielectric of the cable.
    """

    total: float = 0
    """
    The total computed heat transfer in watts for the cable.
    """

    units: str = "W"


class CoaxialCableMaterialSpecificationType(Quantity):
    core: Optional[MaterialReferenceType] = None
    """
    The material of the core.
    """

    sheath: Optional[MaterialReferenceType] = None
    """
    The material of the sheath.
    """

    dielectric: Optional[MaterialReferenceType] = None
    """
    The material of the dielectric.
    """

    def supplied_parameters(self):
        """
        Returns a list of parameter names that have been supplied (i.e., are not None).

        Returns:
            list[str]: A list of parameter names with non-None values.
        """
        values = [
            param
            for param, value in [
                ("core", self.core),
                ("sheath", self.sheath),
                ("dielectric", self.dielectric),
            ]
            if value is not None
        ]
        # print(values)
        return values


class DCCableGeometryType(Quantity):
    core_cross_sectional_area_m2: float = 0
    """
    The cross-sectional area of the core in meters squared.
    """

    length_m: float = 0
    """
    The length of the cable in meters.
    """

    total_cross_sectional_area_m2: float = 0
    """
    The total cross-sectional area of the cable in meters squared.
    """


class DCCableHeatTransferType(Quantity):
    """
    All units are in watts.
    """

    core: Optional[float] = 0
    """
    The computed heat transfer in watts for the core of the cable.
    """

    total: float = 0
    """
    The total computed heat transfer in watts for the cable.
    """

    units: str = "W"


class DCCableMaterialSpecificationType(Quantity):
    core: Optional[MaterialReferenceType] = None
    """
    The material of the core.
    """


class Cable(PhysicalComponent):
    pass


class DCCable(Cable):
    """
    A DC cable is a single core cable that is used to transmit direct current.
    """

    geometry: DCCableGeometryType | None = None
    heat_transfer: DCCableHeatTransferType | None = None
    material_specification: DCCableMaterialSpecificationType | None = None


class CoaxialCable(RFPhysicalComponent):
    """
    A coaxial cable is a type of electrical cable that has an inner conductor surrounded by a tubular insulating layer,
    surrounded by a tubular conducting shield.
    """

    geometry: CoaxialCableGeometryType | None = CoaxialCableGeometryType()
    heat_transfer: Optional[CoaxialCableHeatTransferType] = None
    material_specification: Optional[CoaxialCableMaterialSpecificationType] = None


CableHeatTransferTypes = Union[CoaxialCableHeatTransferType, DCCableHeatTransferType]
CableGeometryTypes = Union[CoaxialCableGeometryType, DCCableGeometryType]
CableMaterialSpecificationTypes = Union[
    CoaxialCableMaterialSpecificationType, DCCableMaterialSpecificationType
]
CableTypes = Union[DCCable, CoaxialCable]
