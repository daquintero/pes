import numpy as np
from typing import Union, List


def get_phasor_length(phasor: Union[int, float, List[float], np.ndarray]) -> int:
    if isinstance(phasor, (list, np.ndarray)):
        return len(phasor)
    elif isinstance(phasor, (int, float)):
        return 1
    else:
        try:
            if isinstance(phasor.magnitude, (list, np.ndarray)):
                return len(phasor.magnitude)
            elif isinstance(phasor.magnitude, (int, float)):
                return 1
            else:
                raise ValueError(f"Unsupported PhasorType: {type(phasor.magnitude)}")
        except AttributeError:
            raise ValueError(f"Unsupported PhasorType: {type(phasor)}")


def offset_path_transmission(path_transmission, offset: float):
    """
    Creates a new PathTransmission with the magnitude of the Phasor at the specified
    index offset by a given value.

    Args:
        path_transmission (PathTransmission): The original PathTransmission instance.
        index (int): The index of the Phasor in the transmission list to apply the offset.
        offset (float): The value to offset the magnitude by.

    Returns:
        PathTransmission: A new PathTransmission instance with the offset applied.
    """
    from piel.types import PathTransmission
    from .core import offset_phasor_magnitude

    assert isinstance(path_transmission, PathTransmission)
    # logger.debug(type(path_transmission))
    # logger.debug(type(path_transmission.transmission))

    # Apply the offset to the specified Phasor in the transmission list
    new_transmission_phasor = offset_phasor_magnitude(
        path_transmission.transmission, offset
    )

    # Create a new PathTransmission with the modified transmission list
    new_path_transmission = PathTransmission(
        connection=path_transmission.connection, transmission=new_transmission_phasor
    )

    return new_path_transmission


def offset_network_transmission_input_magnitude(network_transmission, offset: float):
    """
    Creates a new NetworkTransmission with the magnitude of the specified Phasor offset by a given value.

    Args:
        network_transmission (NetworkTransmission): The original NetworkTransmission instance.
        offset (float): The value to offset the magnitude by.

    Returns:
        NetworkTransmission: A new NetworkTransmission instance with the offset applied.
    """
    from piel.types import NetworkTransmission
    from .core import offset_phasor_magnitude

    # Make a copy of the network list to modify the target PathTransmission
    target_input_offset = network_transmission.input

    # logger.debug(type(target_path))
    offset_input_phasor_i = offset_phasor_magnitude(target_input_offset, offset)

    # Create a new NetworkTransmission with the modified network list and original input
    new_network_transmission = NetworkTransmission(
        input=offset_input_phasor_i,
        network=network_transmission.network,
    )
    # TODO: Verify question mark on immutability with this approach?

    return new_network_transmission


def offset_network_transmission_path_magnitude(
    network_transmission, path_index: int, offset: float
):
    """
    Creates a new NetworkTransmission with the magnitude of the specified Phasor offset by a given value.

    Args:
        network_transmission (NetworkTransmission): The original NetworkTransmission instance.
        path_index (int): The index of the PathTransmission in the network list.
        offset (float): The value to offset the magnitude by.

    Returns:
        NetworkTransmission: A new NetworkTransmission instance with the offset applied.
    """
    from piel.types import NetworkTransmission
    import copy

    new_network_list = copy.deepcopy(network_transmission.network)

    # Make a copy of the network list to modify the target PathTransmission
    target_path_transmission = network_transmission.network[path_index]

    # logger.debug(type(target_path))
    offset_path_transmission_i = offset_path_transmission(
        target_path_transmission, offset=offset
    )

    # Replace the modified PathTransmission in the network list
    new_network_list[path_index] = offset_path_transmission_i

    # Create a new NetworkTransmission with the modified network list and original input
    new_network_transmission = NetworkTransmission(
        input=network_transmission.input, network=new_network_list
    )

    return new_network_transmission
