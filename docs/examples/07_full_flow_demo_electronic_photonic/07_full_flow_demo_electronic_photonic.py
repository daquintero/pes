# # `piel` Electronic-Photonic Co-Design - Full Flow Demo

# <div style="padding: 10px; border-radius: 5px;">
# <strong>⚠️ Warning:</strong> This example requires using the piel nix environment which are locally available when cloning and installing the `stable` verision of the github source code. See example setup as follows
# </div>
#
# Note that this is only CI tested in an ubuntu environment:
# ```
# git clone https://github.com/daquintero/piel.git
# source scripts/install_piel_nix.sh
# ```
#
# You can verify you have the tools required by running the following magic cells:

# ! which openlane

# ```
# /nix/store/9jb8wsk32ny2yy5ghcaq3y7mbmmavi2c-python3.11-openlane/bin/openlane
# ```

# ! which ngspice

# ```
# /nix/store/9jb8wsk32ny2yy5ghcaq3y7mbmmavi2c-python3.11-openlane/bin/openlane
# ```

# ! which gtkwave

# ```
# /nix/store/9jb8wsk32ny2yy5ghcaq3y7mbmmavi2c-python3.11-openlane/bin/openlane
# ```

# The goal of this notebook is to demonstrate some of the codesign functionality in a photonics-first electronically-specified system.
#
#
# <img src="../../_static/img/examples/07_full_flow_demo_electronic_photonic/demo_schematic.png" alt="schematic" width="50%"/>
# <img src="../../_static/img/examples/07_full_flow_demo_electronic_photonic/demo_design_flow.png" alt="design_flow" width="100%"/>

# ## 1a. Configuring our `piel` Project

# You can install `piel` directly via `pip`, or use the provided `uv` lockfile-controlled environment directly from `git`.
#

# All the imports we will need throughout this flows.

# We begin by importing a parametric circuit from `gdsfactory`:
import hdl21 as h
import numpy as np
import pandas as pd
from gdsfactory.generic_tech import get_generic_pdk
import piel
from piel.models.physical.photonic import (
    mzi2x2_2x2_phase_shifter,
    component_lattice_generic,
    straight_heater_metal_simple,
)

# First, let's set up the filesystem in the directory in which all our files will be generated and stored. This is really an extension of a full mixed-signal design compatible with the tools supported by `piel`.

current_example_directory = piel.return_path(".")
piel.create_empty_piel_project(
    project_name="full_flow_demo", parent_directory=current_example_directory
)

# Check out the contents in this file system:

# ! ls full_flow_demo

# ```bash
# docs  full_flow_demo  setup.py
# ```

# ! ls full_flow_demo/full_flow_demo

# ```bash
# analogue    __init__.py  measurement    runs     sdc  tb
# components  io		 photonic  scripts  src
# ```

# Let's install our empty project, before we start generating files now:

# !pip install -e full_flow_demo

# ```bash
# Obtaining file:///home/daquintero/phd/piel/docs/examples/10_demo_full_flow/full_flow_demo
#   Preparing metadata (setup.py) ... done
# Installing collected packages: full_flow_demo
#   Running setup.py develop for full_flow_demo
# Successfully installed full_flow_demo-0.0.1
#
# [notice] A new release of pip is available: 23.0.1 -> 24.0
# [notice] To update, run: pip install --upgrade pip
# ```

# Verify this package is installed:

import full_flow_demo


# ## 1b. Setting up our electro-optic photonic system
#
# The next step is to set up the problem we want to demonstrate. In this example, we will demonstrate the co-design for an electro-optic switch fabric. We will extract the optical logic we want to implement in the fabric and then use that to determine the parameters and design flow of the microelectronics flow.


def create_switch_fabric():
    PDK = get_generic_pdk()
    PDK.activate()
    # CURRENT TODO: Create a basic chain fabric and verify the logic is implemented properly with binary inputs.

    chain_3_mode_lattice = [
        [mzi2x2_2x2_phase_shifter(), 0],
        [0, mzi2x2_2x2_phase_shifter()],
    ]

    chain_3_mode_lattice_circuit = component_lattice_generic(
        network=chain_3_mode_lattice,
    )

    return chain_3_mode_lattice_circuit


chain_3_mode_lattice_circuit = create_switch_fabric()
chain_3_mode_lattice_circuit

# ## 2. Extracting our optical-to-electronic control logic truth table


# We know that we have three optical modes to compute the inputs, and we always are inputting a discrete (on-off) optical pulse on any input. Let's assume our design target is to implement some electronic logic that tries to route the input light down the chain to the very bottom.
#
# Let's implement basic optical switch measurement "1/0" states:

optical_logic_verification_models = piel.models.frequency.get_default_models(
    type="optical_logic_verification"
)
# A specific custom addition to our application:
optical_logic_verification_models["straight_heater_metal_undercut_length200"] = (
    optical_logic_verification_models["straight_heater_metal_undercut"]
)

# Now, we need to compute our transmission information accordingly for a given set of optical inputs:

chain_fock_state_transitions = piel.flows.get_state_phase_transitions(
    circuit_component=chain_3_mode_lattice_circuit,
    models=optical_logic_verification_models,
    switch_states=[0, np.pi],
    mode_amount=3,
    target_mode_index=2,
)

chain_fock_state_transitions.transition_dataframe

# We can plot this to show the electronic-photonic behaviour we want to see:

chain_fock_state_transitions.transmission_data[0].keys()

# Now, we actually need to get the required electronic logic we want to implement, and map it back to a given binary implementation, into a corresponding truth table accordingly.
#
# Let's start by extracting our desired optical logic implementation:

chain_fock_state_transitions.target_output_dataframe

# Now, each of these electronic phases applied correspond to a given digital value that we want to implement on the electronic logic.

basic_ideal_phase_map = piel.models.logic.electro_optic.linear_bit_phase_map(
    bits_amount=5, final_phase_rad=np.pi, initial_phase_rad=0
)
basic_ideal_phase_map.dataframe

# |    |   bits |    phase   |
# |----|--------|------------|
# |  0 |  00000 | 0.000000   |
# |  1 |  00001 | 0.101341   |
# |  2 |  00010 | 0.202681   |
# |  3 |  00011 | 0.304022   |
# |  4 |  00100 | 0.405363   |
# |  5 |  00101 | 0.506703   |
# |  6 |  00110 | 0.608044   |
# |  7 |  00111 | 0.709385   |
# |  8 |  01000 | 0.810726   |
# |  9 |  01001 | 0.912066   |
# | 10 |  01010 | 1.013410   |
# | 11 |  01011 | 1.114750   |
# | 12 |  01100 | 1.216090   |
# | 13 |  01101 | 1.317430   |
# | 14 |  01110 | 1.418770   |
# | 15 |  01111 | 1.520110   |
# | 16 |  10000 | 1.621450   |
# | 17 |  10001 | 1.722790   |
# | 18 |  10010 | 1.824130   |
# | 19 |  10011 | 1.925470   |
# | 20 |  10100 | 2.026810   |
# | 21 |  10101 | 2.128150   |
# | 22 |  10110 | 2.229500   |
# | 23 |  10111 | 2.330840   |
# | 24 |  11000 | 2.432180   |
# | 25 |  11001 | 2.533520   |
# | 26 |  11010 | 2.634860   |
# | 27 |  11011 | 2.736200   |
# | 28 |  11100 | 2.837540   |
# | 29 |  11101 | 2.938880   |
# | 30 |  11110 | 3.040220   |
# | 31 |  11111 | 3.141560   |
#

# We can technically simulate how our optical pulses map to our electronic pulses:

truth_table_full = (
    piel.flows.digital_electro_optic.convert_optical_transitions_to_truth_table(
        optical_state_transitions=chain_fock_state_transitions,
        bit_phase_map=basic_ideal_phase_map,
        logic="full",
    )
)
truth_table_full.dataframe

truth_table = (
    piel.flows.digital_electro_optic.convert_optical_transitions_to_truth_table(
        optical_state_transitions=chain_fock_state_transitions,
        bit_phase_map=basic_ideal_phase_map,
        logic="implementation",
    )
)
truth_table.dataframe

# |    |   input_fock_state_str |   bit_phase_0 |   bit_phase_1 |
# |---:|-----------------------:|--------------:|--------------:|
# |  0 |                    100 |         00000 |         00000 |
# |  1 |                    001 |         00000 |         11111 |
# |  2 |                    010 |         11111 |         00000 |

truth_table.input_ports

truth_table.output_ports

truth_table.implementation_dictionary

# ```
# {'input_fock_state_str': ['100', '001', '010'],
#  'bit_phase_0': ['00000', '00000', '11111'],
#  'bit_phase_1': ['00000', '11111', '00000']}
# ```

# ## 3. Synthesizing the logic, digtial testing and layout implementation

# +
# TODO convert this into a single generic function.
# Inputs truth table, input port list, output port list, module
# No outputs

# Define all the relevant connection from the dictionary

piel.flows.generate_verilog_and_verification_from_truth_table(
    truth_table=truth_table,
    module=full_flow_demo,
)


# -

# ! ls full_flow_demo/full_flow_demo/src

# ```
# truth_table_module.v
# ```

# ! ls full_flow_demo/full_flow_demo/tb

# ```
# __init__.py  __pycache__	       sim_build
# Makefile     results.xml	       test_top.py
# out	     run_cocotb_simulation.sh  truth_table_module.vcd
# ```

# ## 3a. Modelling our implementing digital-to-optical logic


# Because we are using a truth table, we can automatically configure the `cocotb` testing script:

piel.integration.create_cocotb_truth_table_verification_python_script(
    module=full_flow_demo,
    truth_table=truth_table,
    test_python_module_name="test_top",
)

# Now we can run the simulation:

cocotb_simulation_data = piel.flows.run_verification_simulation_for_design(
    module=full_flow_demo,
    top_level_verilog_module="top",
    test_python_module="test_top",
    simulator="icarus",
)
cocotb_simulation_data

# ```bash
# # #!/bin/bash
# # Makefile
# SIM ?= icarus
# TOPLEVEL_LANG ?= verilog
# VERILOG_SOURCES += /home/daquintero/phd/piel/docs/examples/07_full_flow_demo_electronic_photonic/full_flow_demo/full_flow_demo/src/truth_table_module.v
# TOPLEVEL := top
# MODULE := test_top
# include $(shell cocotb-config --makefiles)/Makefile.sim
# Standard Output (stdout):
# # rm -f results.xml
# make -f Makefile results.xml
# make[1]: Entering directory '/home/daquintero/phd/piel/docs/examples/07_full_flow_demo_electronic_photonic/full_flow_demo/full_flow_demo/tb'
# /usr/bin/iverilog -o sim_build/sim.vvp -D COCOTB_SIM=1 -s top  -f sim_build/cmds.f -g2012   /home/daquintero/phd/piel/docs/examples/07_full_flow_demo_electronic_photonic/full_flow_demo/full_flow_demo/src/truth_table_module.v
# # rm -f results.xml
# MODULE=test_top  TESTCASE= TOPLEVEL=top  TOPLEVEL_LANG=verilog  \
#          /usr/bin/vvp -M /home/daquintero/.pyenv/versions/3.10.13/envs/piel_0_57/lib/python3.10/site-packages/cocotb/libs -m libcocotbvpi_icarus   sim_build/sim.vvp
#      -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:105  in set_program_name_in_venv        Using Python virtual environment interpreter at /home/daquintero/.pyenv/versions/3.10.13/envs/piel_0_57/bin/python
#      -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
#      0.00ns INFO     cocotb                             Running on Icarus Verilog version 11.0 (stable)
#      0.00ns INFO     cocotb                             Running tests with cocotb v1.8.1 from /home/daquintero/.pyenv/versions/3.10.13/envs/piel_0_57/lib/python3.10/site-packages/cocotb
#      0.00ns INFO     cocotb                             Seeding Python random module with 1718616475
#      0.00ns INFO     cocotb.regression                  Found test test_top.truth_table_test
#      0.00ns INFO     cocotb.regression                  running truth_table_test (1/1)
#                                                           Test for logic defined by the truth table
#      6.00ns INFO     cocotb.regression                  truth_table_test passed
#      6.00ns INFO     cocotb.regression                  **************************************************************************************
#                                                         ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
#                                                         **************************************************************************************
#                                                         ** test_top.truth_table_test      PASS           6.00           0.01        778.82  **
#                                                         **************************************************************************************
#                                                         ** TESTS=1 PASS=1 FAIL=0 SKIP=0                  6.00           2.33          2.57  **
#                                                         **************************************************************************************
#
# make[1]: Leaving directory '/home/daquintero/phd/piel/docs/examples/07_full_flow_demo_electronic_photonic/full_flow_demo/full_flow_demo/tb'
#
# Standard Error (stderr):
# ```
#
# |    |   Unnamed: 0 |   input_fock_state_str |   bit_phase_0 |   bit_phase_1 |   time |
# |---:|-------------:|-----------------------:|--------------:|--------------:|-------:|
# |  0 |            0 |                    100 |         00000 |         00000 |   2000 |
# |  1 |            1 |                    001 |         00000 |         11111 |   4000 |
# |  2 |            2 |                    010 |         11111 |         00000 |   6000 |
#


# ![example_gtk_wave_signals](../../_static/img/examples/07_full_flow_demo_electronic_photonic/example_gtk_wave_signals.png)

# We could be more ambitious and see how the circuit would progress with a raw set of electronic transitions:

# Now, we could technically also use this simulation to model our optical signal transmission too.

# +
# # Current work in progress move this out of here.
# simple_ideal_o4_mzi_2x2_plots = piel.experimental.plot_simple_multi_row(
#     files=mzi2x2_simple_simulation_data_lines,
#     x_axis_column_name="t",
#     row_list=[
#         "phase_0",
#         "output_amplitude_array_1_abs",
#         "output_amplitude_array_1_phase_deg",
#     ],
#     y_label=["e1 Phase", "o4 Amplitude", "o4 Phase"],
# )
# simple_ideal_o4_mzi_2x2_plots.savefig(
#     "../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o4_mzi_2x2_plots.PNG"
# )

# +
# # Current work in progress move this out of here.
# import pandas as pd
# import sax
# from typing import Callable


# def compute_simulation_unitaries(
#     simulation_data: pd.DataFrame,
#     phase_mapping_function: Callable,
#     data_series_key: str,
#     netlist: dict,
#     model_library: dict,
#     input_ports_order: tuple | None = None,
# ) -> List[Any]:
#     """
#     Processes simulation files to generate a list of unitaries using a digital-to-phase model and a custom library.

#     Args:
#         simulation_data (pd.DataFrame): DataFrame containing simulation files.
#         phase_mapping_function (Callable): Function to map files series to phase array.
#         data_series_key (str): Key to access the specific files series in the simulation files.
#         phase_map (Dict[str, Any]): Additional parameters for phase mapping if required by the function.
#         netlist (Dict[str, Any]): Netlist describing the circuit.
#         custom_model_function (Callable): Function to create a custom model library.
#         library_defaults (Dict[str, Any]): Default parameters for the custom model library.
#         s_parameters_function (Callable): Function to convert model output to S-parameters matrix.
#         input_ports_order (Tuple[str, str]): Order of input connection for the S-parameters function.

#     Returns:
#         List[Any]: List of unitaries corresponding to the phase array.
#     """
#     # Generate phase array using the provided phase mapping function
#     data_series = simulation_data[data_series_key]
#     phase_array = phase_mapping_function(data_series=data_series, phase_map=phase_map)
#     simulation_data["phase"] = phase_array

#     # Create the circuit model using the netlist and custom library
#     circuit_model, _ = sax.circuit(netlist=netlist, measurement=custom_library)

#     # Generate unitaries for each phase in the phase array
#     unitaries = []
#     for phase in phase_array:
#         # Compute the unitary for the current phase
#         unitary = s_parameters_function(circuit_model(sxt={"active_phase_rad": phase}))
#         unitaries.append(unitary)

#     return unitaries


# # def compute_simulation_unitaries():
# # Inputs
# # digital-to-phase model
# # simulation files file
# # sax-circuit-model library
# # output returns list of unitaries accordingly

# # basic_ideal_phase_array = (
# #     piel.measurement.logic.electro_optic.return_phase_array_from_data_series(
# #         data_series=example_simple_simulation_data.x, phase_map=basic_ideal_phase_map
# #     )
# # )

# # example_simple_simulation_data["phase"] = basic_ideal_phase_array
# # example_simple_simulation_data

# # our_custom_library = piel.measurement.frequency.compose_custom_model_library_from_defaults(
# #     {"straight_heater_metal_undercut": straight_heater_metal_simple}
# # )
# # our_custom_library

# # mzi2x2_model, mzi2x2_model_info = sax.circuit(
# #     netlist=mzi2x2_2x2_phase_shifter_netlist, measurement=our_custom_library
# # )
# # piel.tools.sax.sax_to_s_parameters_standard_matrix(mzi2x2_model(), input_ports_order=("o2", "o1"))

# # mzi2x2_active_unitary_array = list()
# # for phase_i in example_simple_simulation_data.phase:
# #     mzi2x2_active_unitary_i = piel.tools.sax.sax_to_s_parameters_standard_matrix(
# #         mzi2x2_model(sxt={"active_phase_rad": phase_i}),
# #         input_ports_order=(def compose_network_matrix_from_models(
# # Compose the netlists as functions
# #             "o2",
# #             "o1",
# #         ),
# #     )
# #     mzi2x2_active_unitary_array.append(mzi2x2_active_unitary_i)


# +
# Inputs
# digital-to-phase model
# simulation files file
# sax-circuit-model library
# output returns list of unitaries accordingly

# basic_ideal_phase_array = (
#     piel.measurement.logic.electro_optic.return_phase_array_from_data_series(
#         data_series=example_simple_simulation_data.x, phase_map=basic_ideal_phase_map
#     )
# )

# example_simple_simulation_data["phase"] = basic_ideal_phase_array
# example_simple_simulation_data

# our_custom_library = piel.measurement.frequency.compose_custom_model_library_from_defaults(
#     {"straight_heater_metal_undercut": straight_heater_metal_simple}
# )
# our_custom_library

# mzi2x2_model, mzi2x2_model_info = sax.circuit(
#     netlist=mzi2x2_2x2_phase_shifter_netlist, measurement=our_custom_library
# )
# piel.tools.sax.sax_to_s_parameters_standard_matrix(mzi2x2_model(), input_ports_order=("o2", "o1"))

# mzi2x2_active_unitary_array = list()
# for phase_i in example_simple_simulation_data.phase:
#     mzi2x2_active_unitary_i = piel.tools.sax.sax_to_s_parameters_standard_matrix(
#         mzi2x2_model(sxt={"active_phase_rad": phase_i}),
#         input_ports_order=(
#             "o2",
#             "o1",
#         ),
#     )
#     mzi2x2_active_unitary_array.append(mzi2x2_active_unitary_i)

# second function up to here

# third function starts here.

# optical_port_input = np.array([1, 0])
# optical_port_input

# example_optical_power_output = np.dot(
#     mzi2x2_simple_simulation_data.unitary.iloc[0][0], optical_port_input
# )
# example_optical_power_output

# output_amplitude_array_0 = np.array([])
# output_amplitude_array_1 = np.array([])
# for unitary_i in mzi2x2_simple_simulation_data.unitary:
#     output_amplitude_i = np.dot(unitary_i[0], optical_port_input)
#     output_amplitude_array_0 = np.append(
#         output_amplitude_array_0, output_amplitude_i[0]
#     )
#     output_amplitude_array_1 = np.append(
#         output_amplitude_array_1, output_amplitude_i[1]
#     )
# output_amplitude_array_0

# mzi2x2_simple_simulation_data["output_amplitude_array_0"] = output_amplitude_array_0
# mzi2x2_simple_simulation_data["output_amplitude_array_1"] = output_amplitude_array_1
# mzi2x2_simple_simulation_data

# mzi2x2_simple_simulation_data_lines = piel.experimental.points_to_lines_fixed_transient(
#     files=mzi2x2_simple_simulation_data,
#     time_index_name="t",
#     fixed_transient_time=1,
# )

# simple_ideal_o3_mzi_2x2_plots = piel.experimental.plot_simple_multi_row(
#     files=mzi2x2_simple_simulation_data_lines,
#     x_axis_column_name="t",
#     row_list=[
#         "phase",
#         "output_amplitude_array_0_abs",
#         "output_amplitude_array_0_phase_deg",
#     ],
#     y_axis_title_list=["e1 Phase", "o3 Amplitude", "o3 Phase"],
# )
# simple_ideal_o3_mzi_2x2_plots.savefig(
#     "../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o3_mzi_2x2_plots.PNG"
# )
# -

# ## 3b. Digital Chip Implementation

component = piel.flows.layout_truth_table(
    truth_table=truth_table,
    module=full_flow_demo,
)

component = piel.flows.get_latest_digital_run_component(
    module=full_flow_demo,
)
component.plot()

print("Truth Table Layout")
component

# ## 4a. Driver-Amplfier Modelling

# Now we will create a amplifier model using `sky130` components.

# toddo add here the example of a simulated spice device.


# ## 4b. Composing and Equivalent-Circuit Modelling

# +

our_resistive_heater_netlist = straight_heater_metal_simple().get_netlist(
    allow_multiple=True, exclude_port_types="optical"
)
# our_resistive_mzi_2x2_2x2_phase_shifter_netlist = our_resistive_mzi_2x2_2x2_phase_shifter.get_netlist(exclude_port_types="optical")
# our_resistive_heater_netlist

our_resistive_heater_spice_netlist = (
    piel.integration.gdsfactory_netlist_with_hdl21_generators(
        our_resistive_heater_netlist
    )
)
our_resistive_heater_spice_netlist


@h.module
class TransientTb:
    """# Basic Extracted Device DC Operating Point Testbench"""

    VSS = h.Port()  # The testbench interface: sole port VSS - GROUND
    VPULSE = h.Vpulse(
        delay=1 * h.prefix.m,
        v1=-1000 * h.prefix.m,
        v2=1000 * h.prefix.m,
        period=100 * h.prefix.m,
        rise=10 * h.prefix.m,
        fall=10 * h.prefix.m,
        width=75 * h.prefix.m,
    )(n=VSS)  # A configured voltage pulse source

    # Our component under test
    dut = example_straight_resistor()
    dut.e1 = VPULSE.p
    dut.e2 = VSS


simple_transient_simulation = piel.tools.hdl21.configure_transient_simulation(
    testbench=TransientTb,
    stop_time_s=200e-3,
    step_time_s=1e-4,
    name="simple_transient_simulation",
)
simple_transient_simulation

piel.tools.hdl21.run_simulation(simple_transient_simulation, to_csv=True)

transient_simulation_results = pd.read_csv("TransientTb.csv")
transient_simulation_results.iloc[20:40]
# -

# ## 5a. Putting it all together

# #### A DAC-Driven Mixed Signal Simulation

# #### Automation

# Now, these transient simulations are something you might want to very configure depending on the type of signals that you might want to verify. However, we can provide some basic parameterised simple functions such as step responses and so on. So instead of having to write everything above, you can also just run the following.

# One desired output of an electrical model simulation is an extraction of the power consumption of the circuit. Fundamentally, this is dependent on the time and the operation performed. Hence, to estimate an average power consumption, it is more effective to define the power consumption of a particular operation, and extract the power consumption for the frequency at which this operation is performed.
#
# In this case, we are defining the energy of the operation at particular nodes of the circuit. For example, we know a resisitve heater will dissipate all of its current consumption as thermal power. However, we also need to evaluate the whole circuit. We can know how much energy our DC or RF power supply is providing by measuring the voltage and current supplied accordingly. In a digital circuit, depending on the frequency of the operation, we know how often there is a signal rise and fall, in both cases forcing digital transistors to operate in the linear regime and consuming more power than in saturation mode. We also need to account the range of time the signals are in saturation mode, as even in CMOS idle state there is a minimal power consumption that is important as the circuit scales into VLSI/EP.
#
# Note that through the SPICE simulations, we can extract the energy required at each operation with greater accuracy than analytically and the complexity of this is configuring the testbench appropriately in order to account for this.

# ## 5b. What comes next?
