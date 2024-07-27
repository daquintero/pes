from typing import Optional
from piel.types import PielBaseModel


class Instance(PielBaseModel):
    """
    This represents the fundamental data structure of an element in connectivity
    """

    name: Optional[str] | None = None


class Port(Instance):
    """
    This represents the fundamental data structure to identify a port.
    """


class Connection(Instance):
    """
    This represents the fundamental data structure to identify a connection between two ports.
    """

    ports: tuple[Port, Port]


class Component(Instance):
    """
    This represents the fundamental data structure to identify a component with ports and internal or external connectivity.
    """

    ports: list[Port]
    connections: list[Connection]