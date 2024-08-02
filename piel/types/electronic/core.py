"""
This module defines files models for low-noise amplifier (LNA) and high-voltage amplifier (HVA) metrics.
It provides structured types using pydantic for validation and includes type aliases for metric ranges.
"""
import gdsfactory as gf
from ..connectivity.physical import PhysicalComponent, PhysicalPort
from ..frequency import RFPhysicalComponent

# Type alias for a photonic circuit component in gdsfactory.
ElectronicCircuitComponent = gf.Component
"""
PhotonicCircuitComponent:
    A type representing a component in a photonic circuit, as defined in the gdsfactory framework.
    This type is used to handle and manipulate photonic components in circuit designs.
"""


class ElectronicCircuit(PhysicalComponent):
    pass


class RFElectronicCircuit(RFPhysicalComponent):
    pass


class Bondpad(PhysicalPort):
    """
    A model representing a bond pad in a photonic circuit.
    """

    pass


class ElectronicChip(PhysicalComponent):
    """
    A model representing an electronic chip in a photonic circuit.
    """

    pass
