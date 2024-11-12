# # Digital & Photonic Cosimulation with `sax` and `cocotb`

# <div style="padding: 10px; border-radius: 5px;">
# <strong>⚠️ Warning:</strong> This example requires the <code>piel-nix</code> tools environment.
# <a href="https://piel.readthedocs.io/en/latest/sections/environment/index.html" target="_blank">See environment configuration documentation</a>.
# </div>

# + active=""
# !git clone https://github.com/daquintero/piel.git
# !cd piel/
# !source scripts/install_piel_nix.sh
# !nix develop .
# -

# We begin by importing a parametric circuit from `gdsfactory`:

from piel.models.physical.photonic import (
    mzi2x2_2x2_phase_shifter,
    mzi2x2_2x2,
    component_lattice_generic,
)
import numpy as np
import jax.numpy as jnp
import piel
import sax
import re
from typing import Callable
from gdsfactory.generic_tech import get_generic_pdk

PDK = get_generic_pdk()
PDK.activate()
piel.visual.activate_piel_styles()

# ## Active MZI 2x2 Phase Shifter

# First, let's look at our actively driven component:

mzi2x2_2x2_phase_shifter()

# ![mzi2x2_2x2_phase_shifter](../_static/img/examples/03a_sax_active_cosimulation/mzi2x2_phase_shifter.PNG)

mzi2x2_2x2_phase_shifter_netlist = mzi2x2_2x2_phase_shifter().get_netlist(
    exclude_port_types="electrical"
)
mzi2x2_2x2_phase_shifter_netlist["instances"].keys()

# ```python
# dict_keys(['bend_euler_1', 'bend_euler_2', 'bend_euler_3', 'bend_euler_4', 'bend_euler_5', 'bend_euler_6', 'bend_euler_7', 'bend_euler_8', 'cp1', 'cp2', 'straight_4', 'straight_5', 'straight_6', 'straight_7', 'straight_8', 'straight_9', 'sxb', 'sxt', 'syl', 'sytl'])
# ```

# From the `mzi2x2_2x2_phase_shifter` component definition, we know that the `sxt` instance in the netlist corresponds to the `straight_heater_metal_simple` actively driven phase shifter in our network.

mzi2x2_2x2_phase_shifter_netlist["instances"]["sxt"]

# So what we do is that if we define an active mode for this waveguide, we can model the network system.

# ## Electronic-to-Phase Mapping
#
# Let us explore first the fundamental relationship between electronic signals to optical phase. When we apply an electronic signal to our actively controlled switches, we expect to change the phase we are applying. The relationship between an electronic signal to the phase strength applied is dependent on the electro-optic modulator tecnology, and this relationship may also be nonlinear. Note that in practice, an analog mapping signal drives the phase transmission of the modulator which requires an analog circuit interconnect which might distort or drift the desired signal to apply. To start, we will explore an ideal digital-to-phase mapping and then extend this system modelling with analog circuit components and performance.
#
# ### Ideal Digital-to-Phase Mapping
#
# For example, assume we have a 4-bit DAC. We know that our applied phase shift $\phi=0$ at our digital code $b0000$. Assume we have an ideal linear phase-shifter that maps the code $b1111$ to $\phi=\pi$. `piel` provides a convenient function to extract this code-to-phase mapping:

basic_ideal_bits_phase_map = piel.models.logic.electro_optic.linear_bit_phase_map(
    bits_amount=5, final_phase_rad=np.pi, initial_phase_rad=0
)
basic_ideal_bits_phase_map.dataframe

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

# This allows us to create an operational model of our phase shifter. It is also possible, that if we have a phase-voltage curve, we can also map that to the analog signal, and the analog signal to the DAC converter accordingly, when a Pandas dataframe is provided.
#
# ### Example simulation from our `cocotb` `simple_design` outputs
#
# We have some bit string simulation results from our `simple_design` `cocotb` simulation which is in the form of a simple Pandas dataframe as discussed in example `docs/examples/02_cocotb_simulation`
#

# !pip install -e designs/simple_design
# you might have to restart your kernel here
import simple_design

cocotb_simulation_output_files = (
    piel.tools.cocotb.get_simulation_output_files_from_design(simple_design)
)
example_simple_truth_table = piel.flows.read_simulation_data_to_truth_table(
    cocotb_simulation_output_files[0],
    input_ports=["a", "b"],
    output_ports=["x"],
)
example_simple_truth_table.dataframe

# |    |   Unnamed: 0 |    a |    b |     x |     t |
# |---:|-------------:|-----:|-----:|------:|------:|
# |  0 |            0 | 0101 | 1010 | 01111 |  2001 |
# |  1 |            1 | 0101 | 1111 | 10100 |  4001 |
# |  2 |            2 | 1000 | 0100 | 01100 |  6001 |
# |  3 |            3 | 1000 | 1000 | 10000 |  8001 |
# |  4 |            4 | 1010 | 1001 | 10011 | 10001 |
# |  5 |            5 | 1011 | 0111 | 10010 | 12001 |
# |  6 |            6 | 1011 | 1100 | 10111 | 14001 |
# |  7 |            7 | 0100 | 1011 | 01111 | 16001 |
# |  8 |            8 | 0011 | 0000 | 00011 | 18001 |
# |  9 |            9 | 0110 | 0101 | 01011 | 20001 |
# | 10 |           10 | 0001 | 1000 | 01001 | 22001 |

# We can get the phase that is mapped to this electronic files accordingly. We can append this into our initial time-domain dataframe:

truth_table = piel.flows.digital_electro_optic.add_truth_table_bit_to_phase_data(
    truth_table=example_simple_truth_table,
    bit_phase_map=basic_ideal_bits_phase_map,
    bit_phase_column_name="x",
)
truth_table.dataframe

# |    |   Unnamed: 0 |    a |    b |     x |     t |   phase_0 |
# |---:|-------------:|-----:|-----:|------:|------:|----------:|
# |  0 |            0 | 0101 | 1010 | 01111 |  2001 |  1.52011  |
# |  1 |            1 | 0101 | 1111 | 10100 |  4001 |  2.02681  |
# |  2 |            2 | 1000 | 0100 | 01100 |  6001 |  1.21609  |
# |  3 |            3 | 1000 | 1000 | 10000 |  8001 |  1.62145  |
# |  4 |            4 | 1010 | 1001 | 10011 | 10001 |  1.92547  |
# |  5 |            5 | 1011 | 0111 | 10010 | 12001 |  1.82413  |
# |  6 |            6 | 1011 | 1100 | 10111 | 14001 |  2.33084  |
# |  7 |            7 | 0100 | 1011 | 01111 | 16001 |  1.52011  |
# |  8 |            8 | 0011 | 0000 | 00011 | 18001 |  0.304022 |
# |  9 |            9 | 0110 | 0101 | 01011 | 20001 |  1.11475  |
# | 10 |           10 | 0001 | 1000 | 01001 | 22001 |  0.912066 |

# This looks like this in GTKWave:

# ![example_simple_design_outputs](../_static/img/examples/02_cocotb_simulation/example_simple_design_outputs.PNG)

# ## Connecting into Active Unitary Calculations

# ### Simple Active 2x2 MZI Phase Shifter

# In order to determine the variation of the unitary dependent on an active phase, we need to first define our circuit model and which phase shifter we would be modulating. We will compose an active MZI2x2 switch based on the decomposition provided by the extracted `sax` netlist. First we determine what are our circuit missing measurement.

sax.get_required_circuit_models(mzi2x2_2x2_phase_shifter_netlist)

# ```['bend_euler', 'mmi2x2', 'straight', 'straight_heater_metal_undercut']```

# We have some basic measurement in `piel` we can use to compose our circuit

all_models = piel.models.frequency.get_all_models()
all_models

straight_heater_metal_simple = all_models["ideal_active_waveguide"]
straight_heater_metal_simple

our_custom_library = piel.models.frequency.compose_custom_model_library_from_defaults(
    {"straight_heater_metal_undercut": straight_heater_metal_simple}
)
our_custom_library

mzi2x2_model, mzi2x2_model_info = sax.circuit(
    netlist=mzi2x2_2x2_phase_shifter_netlist, models=our_custom_library
)
piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mzi2x2_model(), input_ports_order=("o2", "o1")
)

# ```python
# (Array([[-0.3519612 -0.88685119j,  0.11042854+0.27825136j],
#         [-0.11042854-0.27825136j, -0.3519612 -0.88685119j]],      dtype=complex128),
#  ('o2', 'o1'))
# ```

# Because we want to model the phase change applied from our heated waveguide, which we know previously corresponds to the `sxb` instance, we can recalculate our s-parameter matrix according to our applied phase:

piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mzi2x2_model(sxt={"active_phase_rad": np.pi}),
    input_ports_order=(
        "o2",
        "o1",
    ),
)

# ```python
# (Array([[ 0.27825136-0.11042854j,  0.88685119-0.3519612j ],
#         [-0.88685119+0.3519612j ,  0.27825136-0.11042854j]],      dtype=complex128),
#  ('o2', 'o1'))
# ```

# We can clearly see our unitary is changing according to the `active_phase_rad` that we have applied to our circuit.

# #### Digital Data-Driven Active MZI 2x2

# Now we can compute what the unitary of our photonic circuit would be for each of the phases applied in our `cocotb` `simple_design` simulation outputs:

mzi2x2_active_unitary_array = list()
for phase_i in truth_table.dataframe.phase_0:
    mzi2x2_active_unitary_i = piel.tools.sax.sax_to_s_parameters_standard_matrix(
        mzi2x2_model(sxt={"active_phase_rad": phase_i}),
        input_ports_order=(
            "o2",
            "o1",
        ),
    )
    mzi2x2_active_unitary_array.append(mzi2x2_active_unitary_i)

# We can copy this to a new dataframe and append the files in accordingly:

mzi2x2_simple_simulation_data = truth_table.dataframe.copy()
mzi2x2_simple_simulation_data["unitary"] = mzi2x2_active_unitary_array
mzi2x2_simple_simulation_data

# Now we have a direct mapping between our digital state, time, and unitary changes in our `mzi` shifted circuit.

# #### Visualising Photonic and Electronic Data

# ##### Static

# Now we have computed how our photonic circuit changes based on an electronic input. Let us assume we are constantly inputting a power of 1dB on the `o2` top input port of the MZI, and we can measure the optical amplitude on the output.

optical_port_input = np.array([1, 0])
optical_port_input

# Let's run an example:

mzi2x2_simple_simulation_data.unitary.iloc[0]

example_optical_power_output = np.dot(
    mzi2x2_simple_simulation_data.unitary.iloc[0][0], optical_port_input
)
example_optical_power_output

# Now we can calculate this in our steady state in time:

output_amplitude_array_0 = np.array([])
output_amplitude_array_1 = np.array([])
for unitary_i in mzi2x2_simple_simulation_data.unitary:
    output_amplitude_i = np.dot(unitary_i[0], optical_port_input)
    output_amplitude_array_0 = np.append(
        output_amplitude_array_0, output_amplitude_i[0]
    )
    output_amplitude_array_1 = np.append(
        output_amplitude_array_1, output_amplitude_i[1]
    )
output_amplitude_array_0

# ```python
# array([-0.16433296+0.40858838j, -0.29093617+0.49160349j,
#        -0.04479861+0.24660602j, -0.01185814+0.15097517j,
#        -0.00628051-0.0502601j , -0.03387329-0.14756872j,
#        -0.20365313+0.4404957j , -0.09631109+0.3336508j ,
#        -0.24599898+0.46826234j, -0.06834814+0.29143432j,
#        -0.68521404+0.500675)`
#
#
#
# ```

mzi2x2_simple_simulation_data["output_amplitude_array_0"] = output_amplitude_array_0
mzi2x2_simple_simulation_data["output_amplitude_array_1"] = output_amplitude_array_1
mzi2x2_simple_simulation_data

# |    | Unnamed: 0 | a    | b    | x     | t     | phase    | unitary                                                                                                        | output_amplitude_array_0                      | output_amplitude_array_1                   |
# |---:|-----------:|-----:|-----:|------:|------:|---------:|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------|-------------------------------------------|
# |  0 | 0          |  101 | 1010 |  1111 |  2001 | 1.52011  | array([[-0.16426986+0.4086031j ,  0.33489325-0.83300986j],[ 0.33489325-0.83300986j,  0.16426986-0.4086031j ]]), ('o2', 'o1') | -0.16426986489554396+0.40860309522788557j  | 0.3348932484400226-0.8330098644113894j   |
# |  1 | 1          | 1001 | 1001 | 10010 |  4001 | 1.82413  | array([[-0.29089065+0.49165187j,  0.41794202-0.70638908j],[ 0.41794202-0.70638908j,  0.29089065-0.49165187j]]), ('o2', 'o1') | -0.2908906510099731+0.4916518717461718j    | 0.41794202495830884-0.7063890782969602j  |
# |  2 | 2          |    0 | 1011 |  1011 |  6001 | 1.11475  | array([[-0.04476771+0.24661686j,  0.17290701-0.95251202j],[ 0.17290701-0.95251202j,  0.04476771-0.24661686j]]), ('o2', 'o1') | -0.04476771225818654+0.24661685816779796j  | 0.172907011379935-0.9525120170487468j    |
# |  3 | 3          |  100 |  101 |  1001 |  8001 | 0.912066 | array([[-0.01183396+0.1509602j ,  0.07725035-0.98544577j],[ 0.07725035-0.98544577j,  0.01183396-0.1509602j ]]), ('o2', 'o1') | -0.01183396305024137+0.15096020006539462j  | 0.07725035327753166-0.985445766256692j   |
# |  4 | 4          |  101 | 0    | 101   | 10001 | 0.506703 | array([[-0.00628735-0.05025993j, -0.12396978-0.99099238j],[-0.12396978-0.99099238j,  0.00628735+0.05025993j]]), ('o2', 'o1') | -0.006287346214285949-0.050259929453309954j   | -0.12396977624117292-0.9909923830926474j    |
# |  5 | 5          |  11  | 0    | 11    | 12001 | 0.304022 | array([[-0.03390155-0.14758559j, -0.22129543-0.96337818j],[-0.22129543-0.96337818j,  0.03390155+0.14758559j]]), ('o2', 'o1') | -0.03390155326515837-0.14758558714522307j     | -0.22129543393308604-0.963378176041775j     |
# |  6 | 6          |  101 | 1011 | 10000 | 14001 | 1.62145  | array([[-0.20359414+0.44052313j, 0.36681329-0.79368558j],[ 0.36681329-0.79368558j,  0.20359414-0.44052313j]]), ('o2', 'o1')  | -0.2035941443096877+0.4405231323314459j       | 0.36681328554358295-0.7936855849972456j     |
# |  7 | 7          | 1000 | 101  | 1101  | 16001 | 1.31743  | array([[-0.09628268+0.33368601j, 0.25997616-0.90099705j],[ 0.25997616-0.90099705j,  0.09628268-0.33368601j]]), ('o2', 'o1')  | -0.0962826752595154+0.33368600691282485j      | 0.2599761601249619-0.9009970540474179j      |
# |  8 | 8          | 1101 | 100  | 10001 | 18001 | 1.72279  | array([[-0.24594593+0.46830107j, 0.39459122-0.7513338j ],[ 0.39459122-0.7513338j ,  0.24594593-0.46830107j]]), ('o2', 'o1') | -0.24594593237703394+0.46830106903747976j    | 0.3945912222496168-0.7513337969298994j      |
# |  9 | 9          | 1001 | 11   | 1100  | 20001 | 1.21609  | array([[-0.06831739+0.29145769j, 0.21774784-0.92896234j],[ 0.21774784-0.92896234j,  0.06831739+0.29145769j]]), ('o2', 'o1') | -0.0683173918484482+0.2914576912480423j      | 0.21774784446017936-0.9289623374584851j     |
# | 10 | 10         | 1011 | 1111 | 11010 | 22001 | 2.63486  | array([[-0.68513737+0.5007716j , 0.42706175-0.31214236j],[ 0.42706175-0.31214236j,  0.68513737-0.5007716j ]]), ('o2', 'o1') | -0.6851373654811859+0.5007715993013784j      | 0.42706175251351547-0.3121423638257475j     |

# This allows us to plot our optical signal amplitudes in the context of our active unitary variation, we can also simulate how optical inputs that are changing within the state of the unitary affect the total systems. However, for the sake of easy visualisation, we can begin to explore this. Note these results are just for trivial inputs.

# Note that we are trying to plot our signals amplitude, phase in time so it is a three dimensional visualisation.
#
# First, let's transform our complex files into amplitude and phase


mzi2x2_simple_simulation_data["output_amplitude_array_0_abs"] = np.abs(
    mzi2x2_simple_simulation_data.output_amplitude_array_0
)
mzi2x2_simple_simulation_data["output_amplitude_array_0_phase_rad"] = np.angle(
    mzi2x2_simple_simulation_data.output_amplitude_array_0
)
mzi2x2_simple_simulation_data["output_amplitude_array_0_phase_deg"] = np.angle(
    mzi2x2_simple_simulation_data.output_amplitude_array_0, deg=True
)
mzi2x2_simple_simulation_data["output_amplitude_array_1_abs"] = np.abs(
    mzi2x2_simple_simulation_data.output_amplitude_array_1
)
mzi2x2_simple_simulation_data["output_amplitude_array_1_phase_rad"] = np.angle(
    mzi2x2_simple_simulation_data.output_amplitude_array_1
)
mzi2x2_simple_simulation_data["output_amplitude_array_1_phase_deg"] = np.angle(
    mzi2x2_simple_simulation_data.output_amplitude_array_1, deg=True
)
mzi2x2_simple_simulation_data


# We will now convert the files into a plottable form, as when VCD or timing files files are parsed, they assume only a steady point and the plotter includes the lines. However, because we need to account for this type of co-simulation formats, we need to transform the files into a plotting form.

mzi2x2_simple_simulation_data_lines = piel.visual.points_to_lines_fixed_transient(
    data=mzi2x2_simple_simulation_data, time_index_name="t", fixed_transient_time=1
)

# #### Basic Plots
#
# Here we are plotting how the electrical phase applied by the testbench 5-bit digital files, maps onto the optical phase applied on the heated waveguide, and we can use `sax` to measure the optical amplitude and phase at both connection of the MZI2x2.
#
# Note, that for now, we will assume that our applied optical phase is applied onto an ideal phase shifter, where the bandwidth is infinite, and where the applied operation translates to the optical input perfectly. We will make a more realistic time-dependent model of our circuit later.
#
# For the sake of simplicity, we can plot phase and amplitude over time driven by a digitally-encoded applied phase.

simple_ideal_o3_mzi_2x2_plots = piel.visual.plot_simple_multi_row(
    data=mzi2x2_simple_simulation_data_lines,
    x_axis_column_name="t",
    row_list=[
        "phase_0",
        "output_amplitude_array_0_abs",
        "output_amplitude_array_0_phase_deg",
    ],
    y_label=[r"$|e1|$ (abs)", r"$|o3|$ (abs)", r"$deg(o3)$"],
    x_label="time (ns)",
)
simple_ideal_o3_mzi_2x2_plots.savefig(
    "../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o3_mzi_2x2_plots.PNG"
)

# ![simple_ideal_o3_mzi_2x2_plots](../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o3_mzi_2x2_plots.PNG)

simple_ideal_o4_mzi_2x2_plots = piel.visual.plot_simple_multi_row(
    data=mzi2x2_simple_simulation_data_lines,
    x_axis_column_name="t",
    row_list=[
        "phase_0",
        "output_amplitude_array_1_abs",
        "output_amplitude_array_1_phase_deg",
    ],
    y_label=[r"|e1| (abs)", r"$|o4|$ (abs)", r"$deg(o4)$"],
)
simple_ideal_o4_mzi_2x2_plots.savefig(
    "../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o4_mzi_2x2_plots.PNG"
)

# ![simple_ideal_o4_mzi_2x2_plots](../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o4_mzi_2x2_plots.PNG)

# ### Ideal Electronic Load Inaccuracy

# One thing we might want to do is to consider how the total electronic signals vary according to the electrical load that implements our phase shifter operation. In this case, it is a resistive heater. We might want to explore how the RC and heat dissipation dyanamics of our heater affects our full optical switching performance based on our digital input. This is further exemplified in the next example.


# ## Active MZI 2x2 Component Lattice

# Say we have a lattice with two different phase shifters this time. We want to see how the unitary changes when we apply phase control over a different set of parameters.

example_component_lattice = [
    [mzi2x2_2x2_phase_shifter(), 0, mzi2x2_2x2()],
    [0, mzi2x2_2x2(), 0],
    [mzi2x2_2x2(), 0, mzi2x2_2x2_phase_shifter()],
]

mixed_switch_lattice_circuit = component_lattice_generic(
    network=example_component_lattice
)
# mixed_switch_circuit.show()
mixed_switch_lattice_circuit

# ![switch_circuit_plot_widget](../_static/img/examples/03_sax_basics/switch_circuit_plot_widget.PNG)

# ### Model Composition

# +
mixed_switch_lattice_circuit_netlist = piel.tools.gdsfactory.get_netlist_recursive(
    mixed_switch_lattice_circuit, allow_multiple=True
)
top_level_name = (piel.tools.gdsfactory.get_netlist(mixed_switch_lattice_circuit))[
    "name"
]

mixed_switch_lattice_circuit_netlist.keys()
# -

# ```python
# dict_keys(['component_lattice_generic_6555a796', 'mzi_d3794663', 'straight_heater_metal_undercut_length200', 'component_sequence_57aef139', 'via_stack_f7a70c8a', 'mzi_d46c281f'])
# ```
#
# This will exactly vary in your case.

mixed_switch_lattice_circuit_netlist["mzi_d3794663"]["instances"].keys()

# We can check what measurement we need to provide to compose the circuit. In our case, we want to determine all the instances that implement a particular model. This can be built directly into sax.

recursive_composed_required_models = sax.get_required_circuit_models(
    mixed_switch_lattice_circuit_netlist[top_level_name],
    models=piel.models.frequency.get_default_models(),
)
recursive_composed_required_models

# ```python
# ['mzi_d3794663', 'mzi_d46c281f']
# ```
#
# So this tells us all the measurement that are recursively composed, but not inherently provided by our defaults library. These are the measurement we can explore.

recursive_composed_required_models_0 = sax.get_required_circuit_models(
    mixed_switch_lattice_circuit_netlist[recursive_composed_required_models[0]],
    models=piel.models.frequency.get_default_models(),
)
recursive_composed_required_models_0

# ```python
# ['straight_heater_metal_undercut_length200']
# ```

piel.tools.sax.get_component_instances(
    mixed_switch_lattice_circuit_netlist,
    top_level_prefix="mzi_d3794663",
    component_name_prefix=recursive_composed_required_models_0[0],
)

# ```python
# {'straight_heater_metal_undercut_length200': ['sxt']}
# ```

# Now, we know from our example above that we can go deeper down the rabbit hole of iterative measurement until we have provided all measurement for our device. Let's just look at this in practice:

recursive_composed_required_models_0_0 = sax.get_required_circuit_models(
    mixed_switch_lattice_circuit_netlist[recursive_composed_required_models_0[0]],
    models=piel.models.frequency.get_default_models(),
)
recursive_composed_required_models_0_0

# ```python
# ['component_sequence_57aef139', 'taper', 'via_stack_f7a70c8a']
# ```
#
# So this means that all the levels of the model can be composed from our default dictionary.

our_recursive_custom_library = (
    piel.models.frequency.compose_custom_model_library_from_defaults(
        {"straight_heater_metal_undercut_length200": straight_heater_metal_simple}
    )
)
our_recursive_custom_library

# What we can do now is that we can extract what instances use this model.

active_phase_shifters_dictionary = piel.tools.sax.get_component_instances(
    mixed_switch_lattice_circuit_netlist,
    top_level_prefix=top_level_name,
    component_name_prefix=recursive_composed_required_models[0],
)
active_phase_shifters_dictionary

# ```python
# {'mzi_d3794663': ['mzi_1', 'mzi_5']}
# ```

# So these instances are our active phase shifters in our network.

# What `sax.netlist` does, is to map each instance with each component, and then `sax.circuit` maps each component with each model which is then multiplied together.

# ### Controlling our Phase Shifter Instances

# One major complexity we have is that we do not know where our phase shifters are. We can find them in the layout, but we need our algorithm to determine them. There are a few things we know about them for sure. We know that our phase shifter instances begin with `straight_heater_metal_u`. However, we do not yet algorithmically know where they are. We know we can do the following based on our previous analysis. So what we will do now is extract all the active phase shifter components, and their corresponding location within the netlist. Let's remember where we want to end:

(
    mixed_switch_lattice_circuit_s_parameters,
    mixed_switch_lattice_circuit_s_parameters_info,
) = sax.circuit(
    netlist=mixed_switch_lattice_circuit_netlist,
    models=our_recursive_custom_library,
    ignore_missing_ports=True,
)
piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mixed_switch_lattice_circuit_s_parameters()
)
# mzi2x2_model(sxt={"active_phase_rad": phase_i}),

# ```python
# (Array([[ 0.34411686-0.09040629j, -0.11674345-0.17602948j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.21072449+0.01451205j, -0.26493346+0.89644186j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.09765052-0.25443967j,  0.07339689+0.04386991j,
#          -0.25703794+0.90116107j, -0.16029436+0.12066105j],
#         [-0.74559777-0.44564972j,  0.17785668-0.20649981j,
#          -0.18410823-0.07973412j, -0.12933868-0.33796931j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# + active=""
# mixed_switch_lattice_circuit_s_parameters
# -

active_phase_shifters_dictionary[recursive_composed_required_models[0]][0]

piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mixed_switch_lattice_circuit_s_parameters(
        mzi_1={"sxt": {"active_phase_rad": np.pi}}
    )
)

# ```python
# (Array([[-0.14519193-0.15341027j,  0.35452101-0.03007602j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.10733452+0.92858874j, -0.21009279-0.02182726j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.07983096+0.03063805j,  0.1398235 -0.23393281j,
#          -0.25703794+0.90116107j, -0.16029436+0.12066105j],
#         [ 0.1398235 -0.23393281j, -0.65816248-0.56687022j,
#          -0.18410823-0.07973412j, -0.12933868-0.33796931j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# You can clearly see the position and change of the s-parameter matrix accordingly.

piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mixed_switch_lattice_circuit_s_parameters(
        **{
            "mzi_1": {"sxt": {"active_phase_rad": np.pi}},
            "mzi_5": {"sxt": {"active_phase_rad": np.pi}},
        }
    )
)


# ```python
# (Array([[-0.14519193-0.15341027j,  0.35452101-0.03007602j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.10733452+0.92858874j, -0.21009279-0.02182726j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.09765052-0.25443967j, -0.74559777-0.44564972j,
#          -0.19505156-0.04699211j, -0.18536205-0.3107936j ],
#         [ 0.07339689+0.04386991j,  0.17785668-0.20649981j,
#          -0.4077188 +0.84375658j, -0.17860632+0.09139558j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# However, we want to control the phase shifting effect and control the component we are modifying. In our case, we want to modify the phase of the model controlled by our thermo-optic phase shifters which are `straight_heater_metal_s_*` instances. So let's find all the instances and corresponding measurement where there is one of these measurement. We know from the `required_models` function that we are have distinct measurement required for each of these Mach-Zeneder components.

# From this we can tell only of the corresponding instances and submodels. It is important to note that some of the measurement can be composed from other measurement, which means that you need to explore the composition of the internal components potentially if you want to do a full circuit composition verification. What we need to do now, is extract a list of our phase shifters that we can then apply our phase to.

# ### Algorithmically Extracted Phase-Shifter Instances

# So in this example, we're controlling the `sxt: {"active_phase_rad": ourphase}` but this is composed of the `ideal_active_waveguide` model and the corresponding `active_phase_rad` parameter but this is determined from the `mzi_d3794663` definition of the `straight_heater_metal_undercut` phase shifter component. You can see the complexity of the system construction. We can extract all instances that contain this component which are `mzi_1` and `mzi_5`.
#
# However, we want to create a map that returns a phase list in this form:
#
# \begin{equation}
# \left[ \phi \right] = \left[ \phi_0, \phi_1, \phi_2 ... \phi_N \right]
# \end{equation}
#
# However, then we need to determine the index. Let's determine the location of our phase shifter elements in the recursive netlist.


switch_lattice_address = piel.tools.sax.get_matched_model_recursive_netlist_instances(
    recursive_netlist=mixed_switch_lattice_circuit_netlist,
    top_level_instance_prefix="component_lattice_generic",
    target_component_prefix="mzi_d3794663",
    models=piel.models.frequency.get_default_models(),
)
switch_lattice_address

# ```
# [('component_lattice_generic_6555a796', 'mzi_1', 'sxt'),
#  ('component_lattice_generic_6555a796', 'mzi_5', 'sxt')]
# ```

# These keys tell us the location of our phase shifter elements as we have defined in the composition of our component `straight_heater_metal_s` mapping to our `"straight_heater_metal_simple": ideal_active_waveguide` definition in the `piel.measurement.frequency.get_default_models()`. We can use them to compose our phases accordingly as these are hashable elements.

switch_lattice_state_phase = dict()
for switch_lattice_address_i in switch_lattice_address:
    switch_lattice_state_phase.update({switch_lattice_address_i: 0})
switch_lattice_state_phase

# ```python
# {('component_lattice_generic_6555a796', 'mzi_1', 'sxt'): 0,
#  ('component_lattice_generic_6555a796', 'mzi_5', 'sxt'): 0}
# ```

# Let's convert this into a function parameter dictionary that you can use to set the `sax.circuit` function:

example_switch_lattice_function_parameter_dictionary = (
    piel.tools.sax.address_value_dictionary_to_function_parameter_dictionary(
        address_value_dictionary=switch_lattice_state_phase,
        parameter_key="active_phase_rad",
    )
)
example_switch_lattice_function_parameter_dictionary

# ```python
# {'mzi_1': {'sxt': {'active_phase_rad': 0}},
#  'mzi_5': {'sxt': {'active_phase_rad': 0}}}
# ```

# Let's compose our circuit.

(
    mixed_switch_lattice_circuit_s_parameters,
    mixed_switch_lattice_circuit_s_parameters_info,
) = sax.circuit(
    netlist=mixed_switch_lattice_circuit_netlist,
    models=our_recursive_custom_library,
    ignore_missing_ports=True,
)

# We can now do everything we did previously as a function:

piel.tools.sax.sax_to_s_parameters_standard_matrix(
    mixed_switch_lattice_circuit_s_parameters(
        **example_switch_lattice_function_parameter_dictionary
    )
)


# ```python
# (Array([[ 0.34411686-0.09040629j, -0.11674345-0.17602948j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.21072449+0.01451205j, -0.26493346+0.89644186j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.09765052-0.25443967j,  0.07339689+0.04386991j,
#          -0.25703794+0.90116107j, -0.16029436+0.12066105j],
#         [-0.74559777-0.44564972j,  0.17785668-0.20649981j,
#          -0.18410823-0.07973412j, -0.12933868-0.33796931j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# Which matches the values above.

# This is the function we can now use to implement our phase array to phase mapping function.


def switch_lattice_phase_array_to_state(
    circuit: Callable,
    switch_address_list: list,
    phase_array: jnp.ndarray,
    parameter_key: str,
    to_s_parameters_standard_matrix: bool = True,
):
    # Note that the ordered indexing in this case is just done based on the dict.values() iterative decomposition but any specifically ordered implemnetation can be done in this function accordingly for the user.
    # TODO surely there's a faster way to do this. Maybe a Lambda function.
    i = 0
    phase_address_dictionary = dict()

    for switch_address_i in switch_address_list:
        phase_address_dictionary.update({switch_address_i: phase_array[i]})

    # Create a tuple of the corresponding phase shifter positions we can input into other functions.
    phase_address_function_parameter_dictionary = (
        piel.tools.sax.address_value_dictionary_to_function_parameter_dictionary(
            address_value_dictionary=phase_address_dictionary,
            parameter_key=parameter_key,
        )
    )

    # Return the phase shifter controller accordingly
    # Find a way to transform this information into corresponding phases, or maybe map a set of inputs accordingly.
    if to_s_parameters_standard_matrix:
        return piel.tools.sax.sax_to_s_parameters_standard_matrix(
            circuit(**phase_address_function_parameter_dictionary)
        )
    else:
        return circuit(**phase_address_function_parameter_dictionary)


switch_lattice_phase_array_to_state(
    circuit=mixed_switch_lattice_circuit_s_parameters,
    switch_address_list=switch_lattice_address,
    phase_array=jnp.array([0, 0]),
    parameter_key="active_phase_rad",
)

# ```python
# (Array([[ 0.34411686-0.09040629j, -0.11674345-0.17602948j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.21072449+0.01451205j, -0.26493346+0.89644186j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.09765052-0.25443967j,  0.07339689+0.04386991j,
#          -0.25703794+0.90116107j, -0.16029436+0.12066105j],
#         [-0.74559777-0.44564972j,  0.17785668-0.20649981j,
#          -0.18410823-0.07973412j, -0.12933868-0.33796931j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# Verify against previous values:

switch_lattice_phase_array_to_state(
    circuit=mixed_switch_lattice_circuit_s_parameters,
    switch_address_list=switch_lattice_address,
    phase_array=jnp.array([jnp.pi, jnp.pi]),
    parameter_key="active_phase_rad",
)

# ```python
# (Array([[-0.14519193-0.15341027j,  0.35452101-0.03007602j,
#           0.2694585 -0.04083246j, -0.74559777-0.44564972j],
#         [-0.10733452+0.92858874j, -0.21009279-0.02182726j,
#           0.07339689+0.04386991j, -0.09164188-0.25666503j],
#         [ 0.09765052-0.25443967j, -0.74559777-0.44564972j,
#          -0.19505156-0.04699211j, -0.18536205-0.3107936j ],
#         [ 0.07339689+0.04386991j,  0.17785668-0.20649981j,
#          -0.4077188 +0.84375658j, -0.17860632+0.09139558j]],      dtype=complex128),
#  ('in_o_0', 'in_o_1', 'in_o_2', 'in_o_3'))
# ```

# ### Connecting this to our digital simulation

# Follow the flow above:

switch_lattice_simulation_data = truth_table.dataframe.copy()
switch_lattice_active_unitary_array = list()
for phase_i in switch_lattice_simulation_data.phase_0:
    switch_lattice_active_unitary_i = switch_lattice_phase_array_to_state(
        circuit=mixed_switch_lattice_circuit_s_parameters,
        switch_address_list=switch_lattice_address,
        phase_array=jnp.array([phase_i, phase_i]),
        parameter_key="active_phase_rad",
    )
    switch_lattice_active_unitary_array.append(switch_lattice_active_unitary_i)
switch_lattice_simulation_data["unitary"] = switch_lattice_active_unitary_array

switch_lattice_simulation_data["unitary"][0]

# Let's check what happens with our simple output.

optical_port_input = np.array([1, 0, 1, 0])
optical_port_output = dict()
i = 0
for unitary_i in switch_lattice_simulation_data.unitary:
    output_amplitude_i = np.dot(unitary_i[0], optical_port_input)
    for input_port in unitary_i[1]:
        port_id = int(re.search(r"\d+", input_port).group())
        switch_lattice_simulation_data.at[i, "out_o_" + str(port_id)] = (
            output_amplitude_i[port_id]
        )
        switch_lattice_simulation_data.at[i, "out_o_" + str(port_id) + "_abs"] = (
            jnp.abs(output_amplitude_i[port_id])
        )
        switch_lattice_simulation_data.at[i, "out_o_" + str(port_id) + "_phase_rad"] = (
            jnp.angle(output_amplitude_i[port_id])
        )
        switch_lattice_simulation_data.at[i, "out_o_" + str(port_id) + "_phase_deg"] = (
            jnp.angle(output_amplitude_i[port_id], deg=True)
        )
    i += 1
switch_lattice_simulation_data.head()

# |    |   Unnamed: 0 |    a |    b |     x |     t |    phase | unitary                                                                                                                                              | out_o_0                                      | out_o_1                                      | out_o_2                                      | out_o_3                                      |   out_o_0_abs |   output_amplitude_array_0_phase_rad |   output_amplitude_array_0_phase_deg |   out_o_1_abs |   out_o_2_abs |   out_o_3_abs |   out_o_0_phase_rad |   out_o_0_phase_deg |   out_o_1_phase_rad |   out_o_1_phase_deg |   out_o_2_phase_rad |   out_o_2_phase_deg |   out_o_3_phase_rad |   out_o_3_phase_deg |
# |---:|-------------:|-----:|-----:|------:|------:|---------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------|:--------------------------------------------|:--------------------------------------------|:--------------------------------------------|--------------:|------------------------------------:|------------------------------------:|--------------:|--------------:|--------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|
# |  0 |            0 |  101 | 1010 |  1111 |  2001 | 1.52011  | (Array([[-0.15013191+0.15952691j, -0.26976418+0.38134953j,  0.18381716-0.32944468j,  0.5974215 +0.4843307j],   ...   | (0.03368525207042694-0.1699177622795105j) | (0.1888469010591507-0.22879064828157425j) | (-0.5358759462833405-0.24047677218914032j) | (0.7793771773576736-0.9641381502151489j) |     0.173225  |                            -0.663832 |                             -38.0348 |      0.296662 |      0.58736  |       1.23975 |            -1.37509 |            -78.7868 |           -0.88075  |            -50.4633 |            -2.71977 |            -155.832 |           -0.890975 |            -51.0491 |
# |  1 |            1 | 1001 | 1001 | 10010 |  4001 | 1.82413  | (Array([[-0.18857768+0.08340642j, -0.3900405 +0.43822825j,  0.3249085 -0.3075179j ,  0.355272  +0.53568196j], ...   | (0.13633081316947937-0.22411146759986877j) | (0.18533635139465332-0.2901407852768898j)  | (-0.40361288189888-0.2735434025526047j)   | (0.8487350046634674-0.924432098865509j)  |     0.262321  |                            -0.663832 |                             -38.0348 |      0.344284 |      0.487575 |       1.25496 |            -1.02428 |            -58.6871 |           -1.00235  |            -57.4303 |            -2.54596 |            -145.873 |           -0.828063 |            -47.4445 |
# |  2 |            2 |    0 | 1011 |  1011 |  6001 | 1.11475  | (Array([[-0.06703898+0.23669276j, -0.14604962+0.25488028j,  0.02392788-0.23027363j,  0.86039466+0.24353698j],   ...   | (-0.043111104518175125+0.006419122219085693j) | (0.20628974959254265-0.21884635649621487j) | (-0.6855338513851166-0.13816504180431366j) | (0.6745539307594299-0.9816211760044098j) |     0.0435864 |                            -0.663832 |                             -38.0348 |      0.300748 |      0.699318 |       1.19105 |             2.99378 |            171.531  |           -0.814925 |            -46.6918 |            -2.94271 |            -168.605 |           -0.968724 |            -55.5038 |
# |  3 |            3 |  100 |  101 |  1001 |  8001 | 0.912066 | (Array([[-0.01559916+0.2611876j , -0.10576385+0.17564523j,  0.04111886-0.32811826j,  0.13251364+0.21046963j],   ...   | (-0.029729951173067093+0.11906009912490845j)  | (0.19566189497709274-0.23707316990476102j) | (-0.7418899238109589-0.06660886108875275j) | (0.6216734051704407-0.9742364883422852j) |     0.122716  |                            -0.663832 |                             -38.0348 |      0.307388 |      0.744874 |       1.15569 |             1.8155  |            104.02   |           -0.880804 |            -50.4664 |            -3.05205 |            -174.87  |           -1.00282  |            -57.4575 |
# |  4 |            4 |  101 |    0 |   101 | 10001 | 0.506703 | (Array([[ 0.09668259+0.27705616j, -0.07646824+0.00117019j,  0.02333007+0.04225298j,  0.8996601 -0.31036413j],   ...   | (0.12001265957951546+0.31930914148688316j)    | (0.10727294208481908-0.2695584475295618j)  | (-0.8062792718410492+0.10285860300064087j) | (0.5256499610841274-0.9287054538726807j) |     0.341118  |                            -0.663832 |                             -38.0348 |      0.290119 |      0.812814 |       1.06715 |             1.21128 |             69.4012 |           -1.19205  |            -68.2995 |             3.01471 |             172.73  |           -1.05575  |            -60.49   |
#

# ### Plotting Multi-Port Multi-Switch Lattice Data

# Convert to digital equivalent

switch_lattice_simulation_data_lines = piel.visual.points_to_lines_fixed_transient(
    data=switch_lattice_simulation_data, time_index_name="t", fixed_transient_time=1
)

for port_i in range(4):
    switch_lattice_simulation_plots = piel.visual.plot_simple_multi_row(
        data=switch_lattice_simulation_data_lines,
        x_axis_column_name="t",
        row_list=[
            "phase_0",
            "out_o_" + str(port_i) + "_abs",
            "out_o_" + str(port_i) + "_phase_deg",
        ],
        y_label=[
            "e1,5 Phase",
            "o" + str(port_i) + "Amplitude",
            "o" + str(port_i) + "Phase",
        ],
    )
    simple_ideal_o4_mzi_2x2_plots.savefig(
        "../_static/img/examples/03a_sax_active_cosimulation/switch_lattice_simulation_plot_"
        + str(port_i)
        + ".PNG"
    )

# ![switch_lattice_simulation_plot_0](../_static/img/examples/03a_sax_active_cosimulation/switch_lattice_simulation_plot_0.PNG)
# ![switch_lattice_simulation_plot_1](../_static/img/examples/03a_sax_active_cosimulation/switch_lattice_simulation_plot_1.PNG)
# ![switch_lattice_simulation_plot_2](../_static/img/examples/03a_sax_active_cosimulation/switch_lattice_simulation_plot_2.PNG)
# ![switch_lattice_simulation_plot_3](../_static/img/examples/03a_sax_active_cosimulation/switch_lattice_simulation_plot_3.PNG)

# You have the power now.
