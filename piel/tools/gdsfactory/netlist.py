from typing import Literal, Optional
from functools import partial


def get_matched_ports_tuple_index(
    ports_index: dict,
    selected_ports_tuple: Optional[tuple] = None,
    sorting_algorithm: Literal["prefix", "selected_ports"] = "prefix",
    prefix: str = "in",
) -> (tuple, tuple):
    """
        This function returns the input connection of a component. However, input connection may have different sets of prefixes
        and suffixes. This function implements different sorting algorithms for different connection names. The default
        algorithm is `prefix`, which sorts the connection by their prefix. The Endianness implementation means that the tuple
        order is determined according to the last numerical index order of the port numbering. Returns just a tuple of
        the index.
    Returns the indices of connection that match specified criteria. The function supports sorting by a prefix or by a selected tuple of connection.

        Args:
            ports_index (dict): A dictionary where keys are port names and values are their indices.
            selected_ports_tuple (tuple, optional): A tuple of selected connection to match. Defaults to None.
            sorting_algorithm (Literal["prefix", "selected_ports"], optional): The sorting algorithm to use. Defaults to "prefix".
            prefix (str, optional): The prefix to filter connection when using the "prefix" sorting algorithm. Defaults to "in".

        Returns:
            tuple[tuple, tuple]:
                - The first tuple contains the indices of the matched connection in the specified order.
                - The second tuple contains the names of the matched connection in the specified order.

        Raises:
            ValueError: If an unsupported sorting algorithm is specified.

        Examples:
            >>> raw_ports_index = {
            >>>     "in_o_0": 0,
            >>>     "out_o_0": 1,
            >>>     "out_o_1": 2,
            >>>     "out_o_2": 3,
            >>>     "out_o_3": 4,
            >>>     "in_o_1": 5,
            >>>     "in_o_2": 6,
            >>>     "in_o_3": 7,
            >>> }
            >>> get_matched_ports_tuple_index(ports_index=raw_ports_index)
            ((0, 5, 6, 7), ("in_o_0", "in_o_1", "in_o_2", "in_o_3"))
    """
    # TODO optimize this computation
    ports_index_list = list(ports_index.keys())
    matches_ports_index_tuple_order = tuple()
    matched_ports_name_tuple_order = tuple()

    if sorting_algorithm == "prefix":
        matched_ports_list = [
            item for item in ports_index_list if item.startswith(prefix)
        ]
        matched_ports_list.sort()  # Sort the connection numerically by their suffix
        matched_ports_name_tuple_order = tuple(matched_ports_list)
        matches_ports_index_tuple_order = tuple(
            [ports_index[port] for port in matched_ports_list]
        )
    elif sorting_algorithm == "selected_ports":
        if selected_ports_tuple is None:
            raise ValueError(
                "selected_ports_tuple must be provided for 'selected_ports' sorting algorithm."
            )
        matched_ports_name_tuple_order = tuple(selected_ports_tuple)
        matches_ports_index_tuple_order = tuple(
            [ports_index[port] for port in selected_ports_tuple]
        )
    else:
        raise ValueError(f"Sorting algorithm '{sorting_algorithm}' is not defined.")

    return matches_ports_index_tuple_order, matched_ports_name_tuple_order


def get_input_ports_index(
    ports_index: dict,
    sorting_algorithm: Literal["prefix"] = "prefix",
    prefix: str = "in",
) -> tuple:
    """
    This function returns the input connection of a component. However, input connection may have different sets of prefixes
    and suffixes. This function implements different sorting algorithms for different connection names. The default
    algorithm is `prefix`, which sorts the connection by their prefix. The Endianness implementation means that the tuple
    order is determined according to the last numerical index order of the port numbering. Returns the indices and
    names of input connection for a component, sorted by a specified algorithm. The default sorting algorithm uses a prefix.

    Args:
        ports_index (dict): A dictionary where keys are port names and values are their indices.
        sorting_algorithm (Literal["prefix"], optional): The sorting algorithm to use. Defaults to "prefix".
        prefix (str, optional): The prefix to filter and sort connection when using the "prefix" sorting algorithm. Defaults to "in".

    Returns:
        tuple: A tuple where each element is a pair of port index and port name, sorted as specified.

    Examples:
        >>> raw_ports_index = {
        >>>     "in_o_0": 0,
        >>>     "out_o_0": 1,
        >>>     "out_o_1": 2,
        >>>     "out_o_2": 3,
        >>>     "out_o_3": 4,
        >>>     "in_o_1": 5,
        >>>     "in_o_2": 6,
        >>>     "in_o_3": 7,
        >>> }
        >>> get_input_ports_index(ports_index=raw_ports_index)
        ((0, "in_o_0"), (5, "in_o_1"), (6, "in_o_2"), (7, "in_o_3"))
    """
    if sorting_algorithm == "prefix":
        (
            matched_ports_index_tuple,
            matched_ports_name_tuple,
        ) = get_matched_ports_tuple_index(
            ports_index=ports_index, sorting_algorithm=sorting_algorithm, prefix=prefix
        )
        ports_index_order = tuple(
            zip(matched_ports_index_tuple, matched_ports_name_tuple, strict=True)
        )
    else:
        raise ValueError(f"Sorting algorithm '{sorting_algorithm}' is not supported.")

    return ports_index_order


def get_netlist(*args, **kwargs):
    from gdsfactory.get_netlist import get_netlist as get_netlist_raw

    return get_netlist_raw(*args, **kwargs, extend_recursive_port_names=True)


def get_netlist_recursive(*args, **kwargs):
    from gdsfactory.get_netlist import (
        get_netlist_recursive as get_netlist_recursive_raw,
    )

    return get_netlist_recursive_raw(*args, **kwargs, get_netlist_func=get_netlist)
