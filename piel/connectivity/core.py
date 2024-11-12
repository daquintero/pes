import logging
from typing import Optional, Callable
from piel.types import (
    Port,
    Connection,
    PhysicalConnection,
    ConnectionTypes,
    ComponentTypes,
    TimeMetric,
    PhysicalComponent,
)


logger = logging.getLogger(__name__)


__all__ = [
    "create_all_connections",
    "create_component_connections",
    "create_sequential_component_path",
    "create_connection_list_from_ports_lists",
]


def create_all_connections(
    ports: list[Port],
    connection_factory: Optional[Callable[[list[Port]], Connection]] = None,
    connection_type_output: Optional[ConnectionTypes] = Connection,
) -> list[ConnectionTypes]:
    """
    This function receives a list of connection and creates the connections between them as two-port relationships.
    It returns a list of connections. More than two connection can be provided, and it will create all the possible connections.

    Parameters
    ----------
    ports : list[Port]
        The connection list to create connections.

    connection_factory : Optional[Callable[[list[Port]], Connection]], optional
        A function that creates a connection object from a list of connection.
        The function should receive a list of connection and return a connection object.
        If not provided, a default connection factory will be used.
        The default connection factory creates a tuple of connection as a connection object.
        The default is None.

    connection_type_output : Optional[type[Connection]], optional
        The type of connection object to return.

        If not provided, the default connection factory will be used.

        The default is None

    Returns
    -------
    list[Connection]
        A list of connections that were created.
    """

    def default_connection_factory(ports: list[Port, Port]) -> ConnectionTypes:
        """
        This function creates a connection object from a list of connection, by default it creates a tuple of connection as a
        connection object. Should be two connection.
        """
        raw_connection = tuple(ports)

        if type(connection_type_output) is type(Connection):
            connection = Connection(ports=raw_connection)
        elif type(connection_type_output) is type(PhysicalConnection):
            connection = PhysicalConnection(connections=[raw_connection])
        else:
            raise TypeError(
                f"Expected a Connection or PhysicalConnection type, got {type(connection_type_output)} instead."
            )
        return connection

    connection_factory = connection_factory or default_connection_factory

    # Ensure that connection is a list
    if not isinstance(ports, list):
        # Raise descriptive error
        raise TypeError(f"Expected a list of connection, got {type(ports)} instead.")

    connections = []
    for i, port1 in enumerate(ports):
        for port2 in ports[i + 1 :]:
            # Verify port2 is a port
            if not isinstance(port2, Port):
                # Raise descriptive error
                raise TypeError(f"Expected a port, got {type(port2)} instead.")
            else:
                connections.append(connection_factory([port1, port2]))

    return connections


def create_connection_list_from_ports_lists(
    port_connection_list: list[list[Port]],
) -> list[ConnectionTypes]:
    """
    When a list of a list of connection is provided, we construct all the required connections accordingly. TODO more docs.
    """
    connection_list = list()
    for raw_connection_i in port_connection_list:
        connection_list_i = create_all_connections(raw_connection_i)
        connection_list.extend(connection_list_i)

    return connection_list


def create_component_connections(
    components: list[ComponentTypes],
    connection_reference_str_list: list[str] | list[list[str]],
) -> list[ConnectionTypes]:
    """
    The way this function works is by composing the connection namespaces from the names of the components,
    and a given connection dot notation which corresponds to that component.

    Notes
    -----

    The dot notation would be in the format ``"component_1.port1"``. Hence, the input to a connection would be
    ``["component1.port1", "component2.port1"]`` and this function would compile into generating the corresponding
    connection. This is by splitting the component name and port name accordingly and then programmatically acquiring
    the corresponding `Port` reference and creating the `Connection` from this.

    Parameters
    ----------

    components : list[ComponentTypes]
        The components to create connections from.
    connection_reference_str_list : list[str] | list[list[str]]
        The list of strings that represent the connections to create.

    Returns
    -------
    list[ConnectionTypes]
        The list of connections created from the components.
    """
    # Verify the list has at least an element inside it
    if len(connection_reference_str_list) == 0:
        raise ValueError(
            "The list of connection references must have at least one connection."
        )

    # Ensure connection_reference_str_list is a list of lists
    if isinstance(connection_reference_str_list[0], str):
        connection_reference_str_list = [connection_reference_str_list]

    connection_list = []

    for connection_reference in connection_reference_str_list:
        # Ensure each connection reference is a list of two strings
        # TODO extend to more than two strings
        if not isinstance(connection_reference, list) or len(connection_reference) != 2:
            raise ValueError("Each connection reference must be a list of two strings.")

        # Split the connection reference strings into component and port names
        component1_name, port1_name = connection_reference[0].split(".")
        component2_name, port2_name = connection_reference[1].split(".")

        # Initialize connection
        port1 = None
        port2 = None

        # Get the port references
        for component in components:
            if component.name == component1_name:
                port1 = component.get_port(port1_name)
            if component.name == component2_name:
                port2 = component.get_port(port2_name)

        # Check if the connection were found
        if port1 is None or port2 is None:
            raise ValueError(
                f"Could not find the connection for the connection {connection_reference}"
            )

        # Create the connection
        connection = Connection(ports=(port1, port2))
        connection_list.append(connection)

    return connection_list


def create_sequential_component_path(
    components: list[ComponentTypes], name: str = "", **kwargs
) -> ComponentTypes:
    """
    This function takes in a list of components and creates a sequential path connectivity of components with all the connection defined in each component.
    By default, the connectivity will be implemented with the first two connection of the components. There is a clear input and output on each component.
    The timing metric calculations is provided by the timing model of each connection of the component, if there is none defined it will assume a default zero
    time connectivity between the relevant connection. For the output component collection, it will output the timing of the network as a whole based on the
    defined subcomponents.
    This will create an output component with all the subcomponents, TODO more than two connection, and the list of connection

    Creates a sequential path connectivity of components with all the connection defined in each component.

    Parameters:
    -----------
    components : List[ComponentTypes]
          A list of components to be connected sequentially.

    Returns:
    --------
    ComponentTypes
        A new component that encapsulates the sequential path of input components.
    """
    if len(components) < 2:
        raise ValueError(
            "At least two components are required to create a sequential path."
        )

    connections = []
    total_time_value = 0  # = TimeMetric(name=name, attrs={}, value=0, mean=0, min=0, max=0, standard_deviation=0)

    for i in range(len(components) - 1):
        current_component = components[i]
        next_component = components[i + 1]

        # Assume the first port is output and the second is input
        if len(current_component.connection) < 1 or len(next_component.connection) < 1:
            raise ValueError(
                f"Component {current_component.name} or {next_component.name} doesn't have enough connection."
            )

        output_port = current_component.connection[1]
        input_port = next_component.connection[0]

        # Create connection with timing information
        connection_time = (
            output_port.time if hasattr(output_port, "time") else TimeMetric(value=0)
        )
        connection_i = Connection(
            ports=[output_port, input_port],
            time=connection_time,
            name=f"{current_component.name}_to_{next_component.name}",
        )
        physical_connection = PhysicalConnection(connections=[connection_i])
        connections.append(physical_connection)

        # Update total time
        total_time_value += connection_time.value
        # TODO total_time.mean += connection_time.mean
        # TODO total_time.min += connection_time.min
        # TODO total_time.max += connection_time.max
        # Assuming standard deviation is not simply additive

    total_time = TimeMetric(value=total_time_value)
    # TODO implement full network timing analysis

    top_level_ports = [components[0].connection[0], components[-1].connection[-1]]
    # TODO best define top level connection

    top_level_connection = Connection(ports=top_level_ports, time=total_time)
    top_level_physical_connection = PhysicalConnection(
        connections=[top_level_connection]
    )
    # Define abstract path. Note that this is not a physical connection, just that there is a connection path between the connection.
    # TODO this may have to be redefined

    connections.append(top_level_physical_connection)

    ports = [
        components[0].connection[0],
        components[-1].connection[-1],
    ]

    logger.debug(f"Sequential Component connections: {connections}")
    logger.debug(f"Sequential Component components: {components}")
    logger.debug(f"Sequential Component connection: {ports}")

    # Create a new component that encapsulates this path
    path_component = PhysicalComponent(
        ports=ports,  # Input of first, output of last
        components=components,
        connections=connections,
    )

    return path_component


def get_port_index_from_name(port: Port, starting_index: int | None = None) -> int:
    """
    Extracts the numerical index from a port identifier and adjusts based on starting index.
    If port numbering starts at 0, adds 1. If starts at 1 or is None, leaves as is.

    Parameters:
    - port (int or str): The port identifier.
    - starting_index (int, optional): The starting index (0 or 1). Defaults to None.

    Returns:
    - int: The adjusted numerical index of the port.

    Raises:
    - ValueError: If starting_index is not 0, 1, or None.
    - ValueError: If the port string does not contain a numerical index.
    - TypeError: If the port is neither int nor str.
    """
    import re

    if isinstance(port, int):
        port_index = port
    elif isinstance(port, str):
        match = re.search(r"\d+", port)
        if match:
            port_index = int(match.group())
        else:
            raise ValueError(f"Cannot extract port number from string '{port}'")
    else:
        raise TypeError(f"Unsupported port type: {type(port)}. Must be int or str.")

    # Adjust based on starting index
    if starting_index == 0:
        return port_index + 1
    elif starting_index == 1:
        return port_index
    elif starting_index is None:
        return port_index
    else:
        raise ValueError(
            f"Unsupported starting index: {starting_index}. Must be 0 or 1."
        )
