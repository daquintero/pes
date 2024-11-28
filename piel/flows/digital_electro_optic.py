from collections import OrderedDict
import numpy as np
from typing import Optional, Callable
from piel.types import (
    BitPhaseMap,
    BitsType,
    PhaseMapType,
    OpticalStateTransitionCollection,
    TruthTable,
    TruthTableLogicType,
)
from piel.conversion import (
    convert_tuple_to_string,
    convert_to_bits,
)
import logging

logger = logging.getLogger(__name__)


def add_truth_table_bit_to_phase_data(
    truth_table: TruthTable,
    bit_phase_map: BitPhaseMap,
    bit_phase_column_name: str = None,
) -> TruthTable:
    """
    This function converts the bit column of a dataframe into a phase tuple using the phase_bit_dataframe. The
    phase_bit_dataframe is a dataframe that maps the phase to the bit. The phase_series_name is the name of the
    phase series in the phase_bit_dataframe. The bit_series_name is the name of the bit series in the
    phase_bit_dataframe. The bit_column_name is the name of the bit column in the dataframe. The function returns
    a tuple of phases that correspond to the bit column of the dataframe.

    Args:
        truth_table (pd.DataFrame): The dataframe that contains the bit column.
        bit_phase_map (BitPhaseMap): The dataframe that maps the phase to the bit.
        bit_phase_column_name (str): The name of the bit column in the dataframe.

    Returns:
        truth_table (TruthTable): a TruthTable object with the phase columns added.
    """
    if bit_phase_column_name is None:
        bit_phase_column_name = "bits"

    phase_list = []
    # Iterate through the dataframe's phase tuples column
    for bit_phase_i in getattr(
        truth_table, bit_phase_column_name
    ).values():  # TODO update on truth table declaration
        # Convert the bitstrings into a tule of phases
        phase_i = find_nearest_phase_for_bit(bit_phase_i, bit_phase_map)

        # Add the bits to the final list
        phase_list.extend(phase_i)

    phase_tuple = tuple(phase_list)
    # Transpose the phase_tuple using zip(*phase_tuple)
    transposed_phase_tuple = list(zip(*phase_tuple))

    phase_array_length = len(phase_tuple[0])
    for phase_iterable_id_i in range(phase_array_length):
        # Initialise lists
        # TODO auto select which one to implement
        ordered_dict_i = OrderedDict(
            (i, value)
            for i, value in enumerate(transposed_phase_tuple[phase_iterable_id_i])
        )
        setattr(truth_table, f"phase_{phase_iterable_id_i}", ordered_dict_i)

    return truth_table


def add_truth_table_phase_to_bit_data(
    truth_table: TruthTable,
    bit_phase_map: BitPhaseMap,
    phase_column_name: str = None,
    rounding_function: Optional[Callable] = None,
) -> TruthTable:
    """
    This function converts the phase column of a dataframe into a bit tuple using the phase_bit_dataframe. The
    phase_bit_dataframe is a dataframe that maps the phase to the bit. The phase_series_name is the name of the
    phase series in the phase_bit_dataframe. The bit_series_name is the name of the bit series in the
    phase_bit_dataframe. The phase_column_name is the name of the phase column in the dataframe. The function returns
    a tuple of bits that correspond to the phase column of the dataframe.

    Args:
        truth_table (pd.DataFrame): The dataframe that contains the phase column.
        bit_phase_map (BitPhaseMap): The dataframe that maps the phase to the bit.
        rounding_function (Optional[Callable]): The rounding function that is used to round the phase to the nearest
            phase in the phase_bit_dataframe.

    Returns:
        tuple: A tuple of bits that correspond to the phase column of the dataframe.
    """
    if phase_column_name is None:
        phase_column_name = "phase"

    bit_list = []
    # Iterate through the dataframe's phase tuples column
    for phase_tuple in getattr(
        truth_table, phase_column_name
    ):  # TODO update on truth table declaration
        if not isinstance(phase_tuple, BitPhaseMap):
            phase_tuple = tuple([phase_tuple])

        # Convert the tuple of phases into bitstrings using convert_phase_array_to_bit_array
        bits = convert_phase_to_bit_iterable(
            phase_tuple, bit_phase_map, rounding_function
        )

        # Add the bits to the final list
        bit_list.extend(tuple([bits]))

    bits_tuple = tuple(bit_list)
    # Transpose the bits_tuple using zip(*bits_tuple)
    transposed_bits_tuple = list(zip(*bits_tuple))

    phase_bit_array_length = len(bits_tuple[0])
    for phase_iterable_id_i in range(phase_bit_array_length):
        # Initialise lists
        # TODO auto select which one to implement
        # TODO adsuming given ordering
        ordered_dict_i = OrderedDict(
            (i, value)
            for i, value in enumerate(transposed_bits_tuple[phase_iterable_id_i])
        )
        setattr(truth_table, f"bit_phase_{phase_iterable_id_i}", ordered_dict_i)

    return truth_table


def convert_optical_transitions_to_truth_table(
    optical_state_transitions: OpticalStateTransitionCollection,
    bit_phase_map=BitPhaseMap,
    logic: TruthTableLogicType = "implementation",
) -> TruthTable:
    ports_list = optical_state_transitions.keys_list
    output_ports_list = list()
    if logic == "implementation":
        transitions_dataframe = optical_state_transitions.target_output_dataframe
    elif logic == "full":
        transitions_dataframe = optical_state_transitions.transition_dataframe
    else:
        raise ValueError(f"Invalid logic type: {logic}")

    logger.debug(transitions_dataframe["phase"])
    phase_bit_array_length = len(transitions_dataframe["phase"].iloc[0])
    truth_table_raw = dict()

    # Check if all input and output connection are in the dataframe
    for port_i in ports_list:
        truth_table_raw[port_i] = transitions_dataframe.loc[:, port_i].values

        if port_i == "phase":
            continue

        if not isinstance(transitions_dataframe.loc[0, port_i], tuple):
            print(transitions_dataframe.loc[0, port_i])
            continue

        truth_table_raw[f"{port_i}_str"] = transitions_dataframe.loc[:, port_i].apply(
            convert_tuple_to_string
        )

        truth_table_raw[f"{port_i}_str"] = truth_table_raw[f"{port_i}_str"].apply(
            lambda x: "".join(str(x))
        )
        truth_table_raw[f"{port_i}_str"] = truth_table_raw[
            f"{port_i}_str"
        ].values.tolist()

    for phase_iterable_id_i in range(phase_bit_array_length):
        # Initialise lists
        truth_table_raw[f"bit_phase_{phase_iterable_id_i}"] = list()
        output_ports_list.append(f"bit_phase_{phase_iterable_id_i}")

    for transition_id_i in range(len(transitions_dataframe)):
        bit_phase = convert_phase_to_bit_iterable(
            phase=transitions_dataframe["phase"].iloc[transition_id_i],
            bit_phase_map=bit_phase_map,
        )

        for phase_iterable_id_i in range(phase_bit_array_length):
            truth_table_raw[f"bit_phase_{phase_iterable_id_i}"].append(
                bit_phase[phase_iterable_id_i]
            )

    input_ports = ["input_fock_state_str"]
    output_ports = output_ports_list

    truth_table_filtered_dictionary = filter_and_correct_truth_table(
        truth_table_dictionary=truth_table_raw,
        input_ports=input_ports,
        output_ports=output_ports,
    )

    return TruthTable(
        input_ports=input_ports,
        output_ports=output_ports,
        **truth_table_filtered_dictionary,
    )


def convert_phase_to_bit_iterable(
    phase: PhaseMapType,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts a phase array or tuple iterable, into the corresponding mapping of their bitstring
    required within a particular bit-phase mapping. A ``phase_array`` iterable is provided, and each phase is mapped
    to a particular bitstring based on the ``phase_bit_dataframe``. A tuple is composed of strings that represent the
    bitstrings of the phases provided.

    Args:
        phase(Iterable): Iterable of phases to map to bitstrings.
        bit_phase_map(BitPhaseMap): Dataframe containing the phase-bits mapping.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bit_array(tuple): Tuple of bitstrings corresponding to the phases.
    """
    # Determine the maximum length of the bitstrings in the dataframe
    # Assumes last bit phase mapping is the largest one
    max_bit_length = len(bit_phase_map.bits[-1])

    bit_array = []

    for phase_i in phase:
        # Apply rounding function if provided
        if rounding_function:
            phase_i = rounding_function(phase_i)

        # Check if phase is in the dataframe
        matched_rows = bit_phase_map.dataframe.loc[
            bit_phase_map.dataframe["phase"] == phase_i, "bits"
        ]

        # If exact phase is not found, use the nearest phase bit representation
        if matched_rows.empty:
            bitstring, _ = find_nearest_bit_for_phase(
                phase_i, bit_phase_map, rounding_function
            )
        else:
            bitstring = matched_rows.iloc[0]

        # Pad the bitstring to the maximum length
        full_length_bitstring = bitstring.zfill(max_bit_length)

        bit_array.append(full_length_bitstring)

    return tuple(bit_array)


def find_nearest_bit_for_phase(
    target_phase: float,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This is a mapping function between a provided target phase that might be more analogous, with the closest
    bit-value in a `bit-phase` ideal relationship. The error between the target phase and the applied phase is
    limited to the discretisation error of the phase mapping.

    Args:
        target_phase(float): Target phase to map to.
        bit_phase_map(pd.DataFrame): Dataframe containing the phase-bits mapping.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bitstring(str): Bitstring corresponding to the nearest phase.
    """
    # TODO interim pydantic-dataframe migration
    bit_phase_map = bit_phase_map.dataframe

    # Apply rounding function if provided
    if rounding_function:
        target_phase = rounding_function(target_phase)

    # Find the nearest phase from the dataframe
    phases = bit_phase_map["phase"].values
    nearest_phase = phases[
        np.argmin(np.abs(phases - target_phase))
    ]  # TODO implement rounding function here.

    # Get the corresponding bitstring for the nearest phase
    bitstring = bit_phase_map.loc[bit_phase_map["phase"] == nearest_phase, "bits"].iloc[
        0
    ]

    return bitstring, nearest_phase


def find_nearest_phase_for_bit(
    bits: BitsType,
    phase_map: BitPhaseMap,
) -> PhaseMapType:
    """
    Maps a bitstring to the nearest phase(s) in a phase-bit mapping dataframe.

    Args:
        bits (AbstractBitsType): Bitstring to map to a phase.
        phase_map (BitPhaseMap): Dataframe containing the phase-bits mapping.

    Returns:
        Tuple[str, ...]: Tuple of phases or an empty tuple if no match is found.
    """
    bits = convert_to_bits(bits)

    try:
        # Find all phases corresponding to the given bitstring
        matching_phases = phase_map.dataframe.loc[
            phase_map.dataframe["bits"] == bits, "phase"
        ].values

        # Check if any phases were found
        if len(matching_phases) == 0:
            print(f"No phases found for bits: {bits}")
            return tuple()

        # Convert to a tuple
        phase_array = tuple([matching_phases])

        return phase_array
    except Exception as e:
        print(f"An error occurred: {e}")
        return tuple()


def filter_and_correct_truth_table(
    truth_table_dictionary: dict, input_ports: list, output_ports: list
):
    """
    Ensures each unique value of the specified input connection maps to a unique set of values of the output connection.
    If conflicts are found (i.e., the same input maps to different outputs), it retains the first unique mapping.
    It returns a corrected truth table dictionary with only the unique mappings.

    Args:
        input_ports (list of str): List of input port names.
        output_ports (list of str): List of output port names.
        truth_table_dictionary (dict): Dictionary containing input and output files. Keys are port names, and values are lists of values.

    Returns:
        dict: A corrected truth table dictionary with unique mappings.

    Raises:
        ValueError: If input_ports or output_ports are not found in truth_table_dictionary.
    """
    # Ensure the specified connection are in the truth table dictionary
    for port in input_ports + output_ports:
        if port not in truth_table_dictionary:
            raise ValueError(f"Port '{port}' not found in truth_table_dictionary.")

    # Initialize a dictionary to keep track of mappings
    mapping_dict = {}

    # Initialize lists to store the corrected inputs and outputs
    corrected_inputs = {input_port: [] for input_port in input_ports}
    corrected_outputs = {output_port: [] for output_port in output_ports}

    # Get the length of the files lists
    num_entries = len(truth_table_dictionary[input_ports[0]])

    for i in range(num_entries):
        # Extract the current input value
        input_value = tuple(
            truth_table_dictionary[input_port][i] for input_port in input_ports
        )

        # Extract the current set of output values
        output_values = tuple(
            truth_table_dictionary[output_port][i] for output_port in output_ports
        )

        if input_value not in mapping_dict:
            # Store the unique mapping
            mapping_dict[input_value] = output_values
            # Append to the corrected lists
            for input_port, value in zip(input_ports, input_value):
                corrected_inputs[input_port].append(value)
            for output_port, value in zip(output_ports, output_values):
                corrected_outputs[output_port].append(value)

    # Combine the corrected inputs and outputs into a single dictionary
    corrected_truth_table = {**corrected_inputs, **corrected_outputs}

    return corrected_truth_table
