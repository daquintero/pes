import jax.numpy as jnp  # TODO add typing
import logging
from itertools import product
from typing import Optional, Callable, Any
from piel.types import (
    ArrayTypes,
    PhotonicCircuitComponent,
    FockStatePhaseTransition,
    NumericalTypes,
    PhaseTransitionTypes,
    OpticalTransmissionCircuit,
    OpticalStateTransitionCollection,
    SParameterCollection,
    TupleIntType,
)
from piel.conversion import (
    absolute_to_threshold,
    convert_array_type,
)
from ..tools.sax.netlist import (
    address_value_dictionary_to_function_parameter_dictionary,
    get_matched_model_recursive_netlist_instances,
)
from ..tools.sax.utils import sax_to_s_parameters_standard_matrix
from ..tools.qutip import fock_states_only_individual_modes
from ..models.frequency.defaults import get_default_models
from ..integration.thewalrus_qutip import fock_transition_probability_amplitude
from piel.tools.gdsfactory import get_netlist_recursive, get_netlist

logger = logging.getLogger(__name__)


def compose_phase_address_state(
    switch_instance_map: dict,
    switch_phase_permutation_map: dict,
) -> dict:
    """
    This function composes the phase shifter address state for each circuit. This means that we have a dictionary
    that maps the instance address to the phase shifter state. This is then used to compose the function parameter
    state.

    Args:
        switch_instance_map (dict): The dictionary of the switch instances.
        switch_phase_permutation_map (dict): The dictionary of the switch phase permutations.

    Returns:
        phase_shifter_address_state (dict): The dictionary of the phase shifter address state.
    """
    phase_shifter_address_state = dict()
    for i in range(len(switch_phase_permutation_map)):
        phase_shifter_address_state[i] = dict()
        phase_shifter_address_state[i].update(
            {
                instance_address_i: switch_phase_i
                for instance_address_i, switch_phase_i in zip(
                    switch_instance_map,
                    switch_phase_permutation_map[i],
                    strict=False,
                )
            }
        )
    return phase_shifter_address_state


def compose_switch_function_parameter_state(
    switch_phase_address_state: dict,
) -> dict:
    """
    This function composes the combinations of the phase shifter inputs into a form that can be inputted into sax for
    each particular address.

    Args:
        switch_phase_address_state (dict): The dictionary of the switch phase address state.

    Returns:
        phase_shifter_function_parameter_state (dict): The dictionary of the phase shifter function parameter state.
    """

    phase_shifter_function_parameter_state = dict()
    for id_i, phase_address_map in switch_phase_address_state.items():
        phase_shifter_function_parameter_state[id_i] = (
            address_value_dictionary_to_function_parameter_dictionary(
                address_value_dictionary=phase_address_map,
                parameter_key="active_phase_rad",
            )
        )
    return phase_shifter_function_parameter_state


def calculate_switch_unitaries(
    circuit: OpticalTransmissionCircuit,
    switch_function_parameter_state: dict,
) -> SParameterCollection:
    """
    This function calculates the switch unitaries for a given circuit. This means that we iterate over each switch
    function parameter state and we calculate the corresponding unitary matrix.

    Args:
        circuit (OpticalTransmissionCircuit): The optical transmission circuit.
        switch_function_parameter_state (dict): The dictionary of the switch function parameter state.

    Returns:

    """
    implemented_unitary_dictionary = dict()
    for id_i, function_parameter_state_i in switch_function_parameter_state.items():
        sax_s_parameters_i = circuit(**function_parameter_state_i)
        implemented_unitary_dictionary[id_i] = sax_to_s_parameters_standard_matrix(
            sax_s_parameters_i
        )
    return implemented_unitary_dictionary


def calculate_all_transition_probability_amplitudes(
    unitary_matrix: ArrayTypes,
    input_fock_states: list[ArrayTypes],
    output_fock_states: list[ArrayTypes],
) -> dict[int, FockStatePhaseTransition]:
    """
    This tells us the transition probabilities between our photon states for a particular implemented unitary.

    Args:
        unitary_matrix (jnp.ndarray): The unitary matrix.
        input_fock_states (list): The list of input Fock states.
        output_fock_states (list): The list of output Fock states.

    Returns:
        dict[int, FockStatePhaseTransition]: The dictionary of the Fock state phase transition type.
    """
    i = 0
    circuit_transition_probability_data_i = dict()
    for input_fock_state in input_fock_states:
        for output_fock_state in output_fock_states:
            fock_transition_probability_amplitude_i = (
                fock_transition_probability_amplitude(
                    initial_fock_state=input_fock_state,
                    final_fock_state=output_fock_state,
                    unitary_matrix=unitary_matrix,
                )
            )
            data = {
                "input_fock_state": input_fock_state,
                "output_fock_state": output_fock_state,
                "fock_transition_probability_amplitude": fock_transition_probability_amplitude_i,
            }
            circuit_transition_probability_data_i[i] = data
            i += 1
    return circuit_transition_probability_data_i


def calculate_classical_transition_probability_amplitudes(
    unitary_matrix: ArrayTypes,
    input_fock_states: list[ArrayTypes],
    target_mode_index: Optional[int] = None,
    determine_ideal_mode_function: Optional[Callable] = None,
) -> dict:
    """
    This tells us the classical transition probabilities between our photon states for a particular implemented
    s-parameter transformation.

    Note that if no target_mode_index is provided, then the determine_ideal_mode_function will analyse
    the provided files and return the target mode and append the relevant probability files to the files dictionary. It will
    raise an error if no method is implemented.

    Args:
        unitary_matrix (jnp.ndarray): The unitary matrix.
        input_fock_states (list): The list of input Fock states.
        target_mode_index (int): The target mode index.
        determine_ideal_mode_function (Callable): The function that determines the ideal mode.

    Returns:
        dict: The dictionary of the circuit transition probability files.
    """
    circuit_transition_probability_data = {}

    for i, input_fock_state in enumerate(input_fock_states):
        mode_transformation = jnp.dot(unitary_matrix, input_fock_state)
        classical_transition_mode_probability = jnp.abs(
            mode_transformation,
        )  # Assuming probabilities are the squares of the amplitudes TODO recheck

        if target_mode_index is not None:
            logger.debug(classical_transition_mode_probability[target_mode_index])
            if (
                isinstance(
                    classical_transition_mode_probability[target_mode_index],
                    jnp.ndarray,
                )
                and classical_transition_mode_probability[target_mode_index].ndim == 1
            ):
                classical_transition_target_mode_probability = (
                    classical_transition_mode_probability[target_mode_index].item()
                )
            else:
                classical_transition_target_mode_probability = float(
                    classical_transition_mode_probability[target_mode_index]
                )
        elif determine_ideal_mode_function is not None:
            # Determine the ideal mode function and append the relevant probability files to the files dictionary
            target_mode_index = determine_ideal_mode_function(mode_transformation)
            classical_transition_target_mode_probability = (
                classical_transition_mode_probability[target_mode_index]
            )
        else:
            classical_transition_target_mode_probability = None
            logger.debug(
                ValueError(
                    "No target mode index provided and no method to determine it. Will continue."
                )
            )
            pass

        logger.debug(classical_transition_target_mode_probability)

        data = {
            "input_fock_state": input_fock_state,
            "mode_transformation": mode_transformation,
            "classical_transition_mode_probability": classical_transition_mode_probability,
            "classical_transition_target_mode_probability": classical_transition_target_mode_probability,
            "unitary_matrix": unitary_matrix,
        }

        circuit_transition_probability_data[i] = data

    return circuit_transition_probability_data


def construct_unitary_transition_probability_performance(
    unitary_phase_implementations_dictionary: dict,
    input_fock_states: list,
    output_fock_states: list,
) -> dict[int, dict[int, FockStatePhaseTransition]]:
    """
    This function determines the Fock state probability performance for a given implemented unitary. This means we
    iterate over each circuit, then each implemented unitary, and we determine the probability transformation
    accordingly.

    Args:
        unitary_phase_implementations_dictionary (dict): The dictionary of the unitary phase implementations.
        input_fock_states (list): The list of input Fock states.
        output_fock_states (list): The list of output Fock states.

    Returns:
        implemented_unitary_probability_dictionary (dict): The dictionary of the implemented unitary probability.
    """
    implemented_unitary_probability_dictionary = dict()
    for id_i, circuit_unitaries_i in unitary_phase_implementations_dictionary.items():
        implemented_unitary_probability_dictionary[id_i] = dict()
        for id_i_i, implemented_unitaries_i in circuit_unitaries_i.items():
            implemented_unitary_probability_dictionary[id_i][id_i_i] = (
                calculate_all_transition_probability_amplitudes(
                    unitary_matrix=implemented_unitaries_i[0],
                    input_fock_states=input_fock_states,
                    output_fock_states=output_fock_states,
                )
            )
    return implemented_unitary_probability_dictionary


def compose_network_matrix_from_models(
    circuit_component: PhotonicCircuitComponent,
    models: dict,
    switch_states: list,
    top_level_instance_prefix: str = "component_lattice_generic",
    target_component_prefix: str = "mzi",
    netlist_function: Optional[Callable] = None,
    **kwargs,
):
    """
    This function composes the network matrix from the measurement dictionary and the switch states. It does this by first
    composing the switch functions, then composing the switch matrix, then composing the network matrix. It returns
    the network matrix and the switch matrix.

    Args:
        circuit_component (gf.Component): The circuit.
        models (dict): The measurement dictionary.
        switch_states (list): The list of switch states.
        top_level_instance_prefix (str): The top level instance prefix.
        target_component_prefix (str): The target component prefix.
        netlist_function (Optional[Callable]): The netlist function.

    Returns:
        network_matrix (np.ndarray): The network matrix.
    """
    # Compose the netlists as functions
    (
        switch_fabric_circuit,
        switch_fabric_circuit_info_i,
    ) = generate_s_parameter_circuit_from_photonic_circuit(
        circuit=circuit_component,
        models=models,
        netlist_function=netlist_function,
    )

    if netlist_function is None:
        # Generate the netlist recursively
        netlist = get_netlist_recursive(circuit_component, allow_multiple=True)

        switch_instance_list_i = get_matched_model_recursive_netlist_instances(
            recursive_netlist=netlist,
            top_level_instance_prefix=top_level_instance_prefix,
            target_component_prefix=target_component_prefix,
            models=models,
        )

        # Compute corresponding phases onto each switch and determine the output
        switch_fabric_switch_phase_configurations = dict()
        switch_amount = len(switch_instance_list_i)
        switch_instance_valid_phase_configurations_i = []
        logger.debug("switch_states")
        logger.debug(switch_states)
        for phase_configuration_i in product(switch_states, repeat=switch_amount):
            switch_instance_valid_phase_configurations_i.append(phase_configuration_i)

        # Apply corresponding phases onto switches
        switch_fabric_switch_phase_address_state = compose_phase_address_state(
            switch_instance_map=switch_instance_list_i,
            switch_phase_permutation_map=switch_instance_valid_phase_configurations_i,
        )

        switch_fabric_switch_function_parameter_state = (
            compose_switch_function_parameter_state(
                switch_phase_address_state=switch_fabric_switch_phase_address_state
            )
        )

        switch_fabric_switch_unitaries = calculate_switch_unitaries(
            circuit=switch_fabric_circuit,
            switch_function_parameter_state=switch_fabric_switch_function_parameter_state,
        )

    else:
        # TODO fix this hack.
        switch_fabric_switch_function_parameter_state = dict()
        switch_fabric_switch_phase_address_state = list()
        switch_fabric_switch_phase_configurations = dict()
        switch_instance_list_i = list()
        switch_fabric_switch_unitaries = dict()

        id_i = 0
        # TODO check this
        for switch_state_i in switch_states:
            switch_fabric_switch_unitaries[id_i] = sax_to_s_parameters_standard_matrix(
                switch_fabric_circuit(sxt={"active_phase_rad": switch_state_i}),
                input_ports_order=("o2", "o1"),
            )
            switch_fabric_switch_phase_address_state.append(
                {"active_phase_rad": switch_state_i}
            )
            id_i += 1

    return (
        switch_fabric_switch_unitaries,
        switch_fabric_switch_function_parameter_state,
        switch_fabric_switch_phase_address_state,
        switch_fabric_switch_phase_configurations,
        switch_instance_list_i,
        switch_fabric_circuit,
        switch_fabric_circuit_info_i,
    )


def extract_phase_from_fock_state_transitions(
    optical_state_transitions: OpticalStateTransitionCollection,
    transition_type: PhaseTransitionTypes = "cross",
):
    """
    Extracts the phase corresponding to the specified transition type.

    Parameters:
    optical_state_transitions (OpticalStateTransitionCollection): Optical state transitions.
        transition_type (str): Type of transition to extract phase for ('cross' or 'bar').

    Returns:
        float: Phase corresponding to the specified transition type.
    """
    optical_state_transitions = optical_state_transitions.transmission_data
    transition_mapping = {"cross": ((1, 0), (0, 1)), "bar": ((1, 0), (1, 0))}

    if transition_type not in transition_mapping:
        raise ValueError("Invalid transition type. Use 'cross' or 'bar'.")

    input_state, output_state = transition_mapping[transition_type]

    for entry in optical_state_transitions:
        if (
            entry["input_fock_state"] == input_state
            and entry["output_fock_state"] == output_state
        ):
            return entry["phase"][0]

    raise ValueError(f"Phase for the {transition_type} transition not found.")


def extract_phase_tuple_from_phase_address_state(phase_address_state: dict):
    """
    Extracts phase values from a dictionary where keys are tuples representing components and values are the phase values.

    Args:
        phase_address_state (dict): The dictionary with tuple keys representing components and their phase values.

    Returns:
        list of tuples: A list containing tuples of the phase values.
    """
    if isinstance(phase_address_state, dict):
        # Iterate through the dictionary and collect the phase values
        phases = [phase for _, phase in phase_address_state.items()]
    else:
        raise ValueError("Invalid phase address state format.")

    # elif isinstance(phase_address_state, list):
    #     phases = phase_address_state

    return tuple(phases)  # TODO unhack this


def format_electro_optic_fock_transition(
    switch_state_array: ArrayTypes,
    input_fock_state_array: ArrayTypes,
    raw_output_state: ArrayTypes,
    **kwargs,
) -> FockStatePhaseTransition:
    """
    Formats the electro-optic state into a standard FockStatePhaseTransition format. This is useful for the
    electro-optic model to ensure that the output state is in the correct format. The output state is a dictionary
    that contains the phase, input fock state, and output fock state. The idea is that this will allow us to
    standardise and compare the output states of the electro-optic model across multiple formats.

    Args:
        switch_state_array(array_types): Array of switch states.
        input_fock_state_array(array_types): Array of valid input fock states.
        raw_output_state(array_types): Array of raw output state.
        **kwargs: Additional keyword arguments.

    Returns:
        electro_optic_state(FockStatePhaseTransition): Electro-optic state.
    """
    electro_optic_state = {
        "phase": convert_array_type(switch_state_array, "tuple"),
        "input_fock_state": convert_array_type(input_fock_state_array, TupleIntType),
        "output_fock_state": absolute_to_threshold(
            raw_output_state, output_array_type=TupleIntType
        ),
        **kwargs,
    }
    # assert isinstance(electro_optic_state, FockStatePhaseTransition) # TODO FIX ME
    return electro_optic_state


def generate_s_parameter_circuit_from_photonic_circuit(
    circuit: PhotonicCircuitComponent,
    models: Any = None,  # sax.modelfactory
    netlist_function: Optional[Callable] = None,
) -> tuple[any, any]:
    """
    Generates the S-parameters and related information for a given circuit using SAX and custom measurement.

    Args:
        circuit (gf.Component): The circuit for which the S-parameters are to be generated.
        models (sax.ModelFactory, optional): The measurement to be used for the S-parameter generation. Defaults to None.
        netlist_function (Callable, optional): The function to generate the netlist. Defaults to None.

    Returns:
        tuple[any, any]: The S-parameters circuit and related information.
    """
    import sax

    # Step 1: Retrieve default measurement if not provided
    if models is None:
        models = get_default_models()

    if netlist_function is None:
        # Step 2: Generate the netlist recursively
        netlist = get_netlist_recursive(circuit, allow_multiple=True)
    else:
        netlist = netlist_function(circuit)

    try:
        # Step 7: Compute the S-parameters using the custom library and netlist
        s_parameters, s_parameters_info = sax.circuit(
            netlist=netlist,
            models=models,
            ignore_missing_ports=True,
        )
    except Exception as e:
        """
        Custom exception mapping.
        """
        # Step 3: Identify the top-level circuit name
        top_level_name = get_netlist(circuit)["name"]

        # Step 4: Get required measurement for the top-level circuit
        required_models = sax.get_required_circuit_models(
            netlist[top_level_name], models=models
        )

        specific_model_key = [
            model
            for model in required_models
            if model.startswith(
                "mzi"
            )  # should technically be the top level recursive component
        ][0]

        specific_model_required = sax.get_required_circuit_models(
            netlist[specific_model_key],
            models=models,
        )
        logger.error("Error in generating S-parameters. Check the following:")
        logger.error("Required measurement for the top-level circuit:")
        logger.error(required_models)
        logger.error("Required measurement for the specific model:")
        logger.error(specific_model_key)
        logger.error("Required measurement for the specific model:")
        logger.error(specific_model_required)

        raise e

    return s_parameters, s_parameters_info


def get_state_phase_transitions(
    circuit_component: PhotonicCircuitComponent,
    models: dict = None,
    mode_amount: int = None,
    input_fock_states: list[ArrayTypes] | None = None,
    switch_states: list[NumericalTypes] | None = None,
    determine_ideal_mode_function: Optional[Callable] = None,
    netlist_function: Optional[Callable] = None,
    target_mode_index: Optional[int] = None,
    **kwargs,
) -> OpticalStateTransitionCollection:
    """
    The goal of this function is to extract the corresponding phase required to implement a state transition.

    Let's consider a simple MZI 2x2 logic with two transmission states. We want to verify that the electronic function
    switch, effectively switches the optical output between the cross and bar states of the optical transmission function.

    For the corresponding switch model:

    Let's assume a switch model unitary. For a given 2x2 input optical switch "X". In bar state, in dual rail, transforms an optical input:
    ```
    .. raw::

        [[1] ----> [[1]
        [0]]        [0]]

    In cross state, in dual rail, transforms an optical input:

    .. raw::

        [[1] ----> [[0]
        [0]]        [1]]

    However, sometimes it is easier to describe a photonic logic transformation based on these states, rather than inherently
    the numerical phase that is applied. This may be the case, for example, in asymmetric Mach-Zehnder modulators measurement, etc.

    As such, this function will help us extract the corresponding phase for a particular switch transition.

    When the switch function is larger than a single switch, it is necessary to extract the location of the corresponding switches as function parameters.
    """
    # We compose the fock states we want to apply
    if input_fock_states is None:
        input_fock_states = fock_states_only_individual_modes(
            mode_amount=mode_amount,
            maximum_photon_amount=1,
            output_type="jax",
        )

    output_states = list()

    _ = (
        circuit_unitaries,
        circuit_function_parameter_state,
        circuit_phase_address_state,
        circuit_phase_configurations,
        instance_list_i,
        fabric_circuit,
        fabric_circuit_info_i,
    ) = compose_network_matrix_from_models(
        circuit_component=circuit_component,
        models=models,
        switch_states=switch_states,
        netlist_function=netlist_function,
        **kwargs,
    )

    id_i = 0
    for unitary_i, _ in circuit_unitaries.values():
        data_i = calculate_classical_transition_probability_amplitudes(
            unitary_matrix=unitary_i,
            input_fock_states=input_fock_states,
            target_mode_index=target_mode_index,
            determine_ideal_mode_function=determine_ideal_mode_function,
        )

        for id_i_i, _ in data_i.items():
            logger.debug(data_i[id_i_i]["classical_transition_target_mode_probability"])
            logger.debug(
                jnp.round(
                    data_i[id_i_i]["classical_transition_target_mode_probability"]
                )
            )
            output_state_i = format_electro_optic_fock_transition(
                switch_state_array=extract_phase_tuple_from_phase_address_state(
                    circuit_phase_address_state[id_i]
                ),
                input_fock_state_array=data_i[id_i_i]["input_fock_state"],
                raw_output_state=data_i[id_i_i][
                    "classical_transition_mode_probability"
                ],
                target_mode_output=int(
                    jnp.round(
                        data_i[id_i_i]["classical_transition_target_mode_probability"]
                    )
                )
                if data_i[id_i_i]["classical_transition_target_mode_probability"]
                is not None
                else None,  # set if available otherwise None,
                raw_output=data_i[id_i_i]["classical_transition_mode_probability"]
                if data_i[id_i_i]["classical_transition_mode_probability"] is not None
                else None,
                unitary=unitary_i,
            )
            output_states.append(output_state_i)
        id_i += 1

    output_optical_state_transitions = OpticalStateTransitionCollection(
        mode_amount=mode_amount,
        target_mode_index=target_mode_index,
        transmission_data=output_states,
    )

    return output_optical_state_transitions


def get_state_to_phase_map(
    switch_function: OpticalTransmissionCircuit,
    switch_states: list[NumericalTypes] | None = None,
    input_fock_states: list[ArrayTypes] | None = None,
    target_transition_list: list[dict] | None = None,
    mode_amount: int | None = None,
    **kwargs,
) -> tuple[ArrayTypes]:
    """
    The goal of this function is to extract the corresponding phase required to implement a state transition.

    Let's consider a simple MZI 2x2 logic with two transmission states. We want to verify that the electronic function
    switch, effectively switches the optical output between the cross and bar states of the optical transmission function.

    For the corresponding switch model:

    Let's assume a switch model unitary. For a given 2x2 input optical switch "X". In bar state, in dual rail, transforms an optical input:
    ```
    .. raw::

        [[1] ----> [[1]
        [0]]        [0]]

    In cross state, in dual rail, transforms an optical input:

    .. raw::

        [[1] ----> [[0]
        [0]]        [1]]

    However, sometimes it is easier to describe a photonic logic transformation based on these states, rather than inherently
    the numerical phase that is applied. This may be the case, for example, in asymmetric Mach-Zehnder modulators measurement, etc.

    As such, this function will help us extract the corresponding phase for a particular switch transition.
    """
    state_phase_transition_list = get_state_phase_transitions(
        circuit_transmission_function=switch_function,
        mode_amount=mode_amount,
        input_fock_states=input_fock_states,
        switch_states=switch_states,
        **kwargs,
    )
    # TODO implement the extraction from mapping the target fock states to the corresponding phase in more generic way
    cross_phase = extract_phase_from_fock_state_transitions(
        state_phase_transition_list, transition_type="cross"
    )
    bar_phase = extract_phase_from_fock_state_transitions(
        state_phase_transition_list, transition_type="bar"
    )
    return bar_phase, cross_phase
