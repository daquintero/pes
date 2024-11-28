# # Interconnection Modelling & Experimental Analysis
#
# It is very difficult to design an electronic-photonic system without actually *connecting* them together. As it turns out, interconnection modelling is crucial in understanding the scaling of these systems.
#
# We might want to model:
#
# - Interconnection effects of electro-optic switches with their transmission line, or transmission lines towards RF analog modulation
# - Path-length matched digital transmission lines to an amplifier
# - The transmission line from a detector diode to the low-noise amplifier before an analogue-to-digital converter.
# - Electronic to photonic chip bonding.
#
# An important aspect to note is that the computational architecture is designed to have the minimal amouunt of operations being computed for a given type of modelling, and this means the modelling speed is as fast as can be for a given operation within a python implementation, pending further toolset implementations.
#
# As such, understanding interconnection effects turns out to be pretty important in these type of systems.

# +
import piel
import piel.experimental as pe
import piel.visual as pv
from piel.models.physical.electrical.cables.rf import (
    calculate_coaxial_cable_geometry,
    calculate_coaxial_cable_heat_transfer,
)
from piel.models.physical.electrical.cables.dc import (
    calculate_dc_cable_geometry,
)
from piel.types.electrical.cables import (
    CoaxialCableMaterialSpecificationType,
)

import matplotlib.pyplot as plt
import pandas as pd
import skrf
from skrf.io.touchstone import hfss_touchstone_2_network
from skrf.plotting import stylely
import os
# -

# ## Basic Thermal Modelling

# ### Modelling a DC Wire
#
# Let's take the most basic example to physically verify that the numerical functional implementation gives accurate results in terms of calculating the corresponding heat transfer. We will also do some analytical comparisons:

basic_dc_cable = calculate_dc_cable_geometry(
    length_m=1,
    core_diameter_m=1e-3,
)
basic_dc_cable

# ### Modelling a Coaxial Cable
#
# #### Thermal Heat Transfer
#
# Note that we have strongly-typed classes in order to manage the files containers across multiple functions. This enables flexibly extending the corresponding implementations.

basic_coaxial_cable = calculate_coaxial_cable_geometry(
    length_m=1,
    sheath_top_diameter_m=1.651e-3,
    sheath_bottom_diameter_m=1.468e-3,
    core_diameter_m=2e-3,
)
basic_coaxial_cable

# ```
# CoaxialCableGeometryType(core_cross_sectional_area_m2=3.141592653589793e-06, length_m=1.0, sheath_cross_sectional_area_m2=4.482872075095052e-07, total_cross_sectional_area_m2=3.5898798610992983e-06)
# ```

# You can also run the help function to learn more of the corresponding class, on top of the existing documentation.

# +
# help(CoaxialCableGeometryType)
# -

# Now, let's apply each section with materials. First, let's work out what are all the current supported materials specifications (feel free to contribute!). Note that this is always specific to the corresponding property.

from piel.materials.thermal_conductivity import (
    material_references as thermal_conductivity_material_references,
)

thermal_conductivity_material_references

# ```
# [('stainless_steel', '304'),
#  ('stainless_steel', '310'),
#  ('stainless_steel', '316'),
#  ('aluminum', '1100'),
#  ('copper', 'rrr50'),
#  ('copper', 'rrr100'),
#  ('copper', 'rrr150'),
#  ('copper', 'rrr300'),
#  ('copper', 'rrr500'),
#  ('teflon', None)]
# ```

# It is pretty straightforward to define a corresponding coaxial-cable material specification accordingly with the static `CoaxialCableMaterialSpecificationType` container:

basic_coaxial_cable_materials = CoaxialCableMaterialSpecificationType(
    core=("copper", "rrr50"), sheath=("copper", "rrr50"), dielectric=("teflon", None)
)
basic_coaxial_cable_materials

# ```
# CoaxialCableMaterialSpecificationType(core=('copper', 'rrr50'), sheath=('copper', 'rrr50'), dielectric=('teflon', None))
# ```

# Now, let's assume we have a coaxial cable that goes from room temperature to cryogenic temperatures. Say, a cable inside a cryostat that goes from 273K to 70K. Let's work out how much thermal heat transfer occurs in between these stages in Watts.

temperature_range_limits_K = tuple([70, 273])

# help(calculate_coaxial_cable_heat_transfer)

basic_coaxial_cable_heat_transfer = calculate_coaxial_cable_heat_transfer(
    temperature_range_K=temperature_range_limits_K,
    geometry_class=basic_coaxial_cable,
    material_class=basic_coaxial_cable_materials,
)
basic_coaxial_cable_heat_transfer

# ```
# CoaxialCableHeatTransferType(core=0.0019091610845816964, sheath=0.0019091610845816964, dielectric=0.00018867678408072714, total=0.00400699895324412)
# ```

# ### Larger System Modelling

# Modelling the heat transfer of multiple coaxial cables in parallel in a system involves basic python operations:s

parallel_cables_amount = 4
4 * basic_coaxial_cable_heat_transfer.total

# ```
# 0.01602799581297648
# ```

# Modelling the heat transfer of 4 cables in series, just involves making the cable in series:

# +
basic_coaxial_cable_4_in_series = calculate_coaxial_cable_geometry(
    length_m=1 * 4,
    sheath_top_diameter_m=1.651e-3,
    sheath_bottom_diameter_m=1.468e-3,
    core_diameter_m=2e-3,
)

basic_coaxial_cable_heat_transfer_4_in_series = calculate_coaxial_cable_heat_transfer(
    temperature_range_K=temperature_range_limits_K,
    geometry_class=basic_coaxial_cable_4_in_series,
    material_class=basic_coaxial_cable_materials,
)
basic_coaxial_cable_heat_transfer_4_in_series
# -

# ```
# CoaxialCableHeatTransferType(core=0.0004772902711454241, sheath=0.0004772902711454241, dielectric=4.7169196020181784e-05, total=0.00100174973831103)
# ```

# Note that when modelling the heat transfer through one of these cables, it is also interesting to relate this to the rf performance of the cables.

# ## RF Modelling and Experimental Relationship

# In the following section of this example, we will explore some basic principles of RF transmission line measurements in the context of both measurement measurements and larger system modelling. We will really explore some basic RF principles and how these can be represented with open-source toolsets using `piel`.
#
# A very common package to model radio-frequency systems in python is called [`scikit-rf`](https://scikit-rf.readthedocs.io/en/latest/index.html). Particularly, it has a lot of useful functionality to translate IO files directly from common measurement standards in a format that is useful for device characterization and modelling. We will explore some basic situations commonly used throughout modelling `rf-photonic` systems.
#
# As far as I can tell from basic usage, the only useful files are one-port `.s1p` and two-port`.s2p` Touchstone files for trace measurements, and `.cti` files for calibration/instrument settings storage. We will use `.s2p` files throughout primarily.

# We will also explore how to manage the way the data is being saved with measurement planning and design.

# ### Understanding Hardware and Software Measurements & Calibration

# A very common procedure when doing a measurement with a vector-network-analyser (VNA) is to perform calibration, also called de-embedding. This is to move the measurement plane from the VNA up to the device-under-test (DUT) and is necessary for accurate measurements of our devices.
#
# There are multiple ways to implement de-embedding or calibration in practice. Most VNAs will have some protocol encoded in their internal firmware/software to implement this. Other ways to do this are using software packages such as `scikit-rf`. Let's set up a measurement experiment to understand the accuracy of either implementation.
#
# Alongside the equipment calibration manual, some good references about this are:
#
# 1. Lourandakis, E. (2016). On-wafer microwave measurements and de-embedding. Artech House.
# 2. Pozar, D. M. (2000). Microwave and RF design of wireless systems. John Wiley & Sons.
#
# An important aspect to keep track of things is the configuration of the VNA.

# ## Frequency-Domain Analysis
#
# ## Performing the VNA/Deembedding Calibration
#
# We will use the calibration kit of an Agilent E8364A PNA which is nominally designed for 2.4mm coaxial cables. Using 2.4mm to 3.5mm SMA adapters is probably fine given that we're deembedding up to a given cable. Realistically, I would need to deembed the performance of the adapter between the calibration kit and the open, short, through adapter.

# ### Using a Hardware Calibration Kit
#
# Decide the two reference points at which you will connect to your device to test. This is a very common way to start doing de-embedding on a machine. In our setup, we will use the Agilent 82052D 3.5mm calibration kit. We can easily follow the instructions using our E8364A Agilent PNA. Let's assume this has been done correctly.
#
# So, we have performed the calibration of our measurement using that calibration kit. In our case, we will perform the first hardware calibration up to the black tongs as shown in the figure below.

# Let's compose the experiment into a correct format. First let's create our components.

short_1port = piel.models.physical.electrical.short_85052D()
load_1port = piel.models.physical.electrical.load_85052D()
open_1port = piel.models.physical.electrical.load_85052D()
throguh_2port = piel.models.physical.electrical.through_85052D()

# We can create our `VNA` and a standard configuration too:

vna_configuration = pe.types.VNAConfiguration(calibration_setting_name="bpl_vna_ports")
vna = piel.models.physical.electrical.E8364A(configuration=vna_configuration)

vna_configuration

# We can explore the parameters of these components to understand their configuration and information

vna

short_1port


def one_port_measurement_configuration(
    one_port_component, vna, measurement_type, calibration
):
    # Note that each measurement can be considered an experiment instance
    experiment_instances = list()
    parameters = list()

    # First we instantiate our short calibration connector and our VNA
    components = [one_port_component, vna]

    # We need to create connections between PORT1 and PORT2 accordingly, note that we need to calibrate both VNA connection.
    vna_port1_connections = piel.create_component_connections(
        components=components,
        connection_reference_str_list=[
            f"{vna.name}.PORT1",
            f"{one_port_component.name}.IN",
        ],
    )

    vna_port2_connections = piel.create_component_connections(
        components=components,
        connection_reference_str_list=[
            f"{vna.name}.PORT2",
            f"{one_port_component.name}.IN",
        ],
    )

    # Create the required experiment instances
    i = 1
    for connections_i in [vna_port1_connections, vna_port2_connections]:
        experiment_instance_i = pe.types.ExperimentInstance(
            name=f"{measurement_type}_port_{i}",
            components=components,
            connections=connections_i,
            measurement_configuration_list=[
                pe.types.VNASParameterMeasurementConfiguration()
            ],
        )
        experiment_instances.append(experiment_instance_i)

        parameters += [
            {"port": i, "measurement": measurement_type, "calibration": calibration}
        ]

        i += 1

    return experiment_instances, parameters


# We need to do a similar thing with the remaining one connection, so let's run this now.

short_experimental_instance_list, short_parameters_list = (
    one_port_measurement_configuration(short_1port, vna, "short", "vna_ports")
)
open_experimental_instance_list, open_parameters_list = (
    one_port_measurement_configuration(open_1port, vna, "open", "vna_ports")
)
load_experimental_instance_list, load_parameters_list = (
    one_port_measurement_configuration(load_1port, vna, "load", "vna_ports")
)


def two_port_measurement_configuration(
    two_port_component, vna, measurement_type, calibration
):
    # First we instantiate our short calibration connector and our VNA
    components = [two_port_component, vna]
    port = "12"

    # We need to create connections between PORT1 and PORT2 accordingly, note that we need to calibrate both VNA connection.
    vna_connections = piel.create_component_connections(
        components=components,
        connection_reference_str_list=[
            [f"{vna.name}.PORT1", f"{two_port_component.name}.IN"],
            [f"{vna.name}.PORT2", f"{two_port_component.name}.OUT"],
        ],
    )

    # Create the required experiment instance
    experiment_instance = pe.types.ExperimentInstance(
        name=f"{measurement_type}_port_{port}",
        components=components,
        connections=vna_connections,
        measurement_configuration_list=[
            pe.types.VNASParameterMeasurementConfiguration()
        ],
    )

    parameters = [
        {"port": port, "measurement": measurement_type, "calibration": calibration}
    ]

    return experiment_instance, parameters


through_experiment_instance, through_parameters = two_port_measurement_configuration(
    throguh_2port, vna, "through", "vna_ports"
)


# Let's define all our relevant `ExperimentInstance`:

vna_self_calibration_experiment_instances = (
    [through_experiment_instance]
    + open_experimental_instance_list
    + load_experimental_instance_list
    + short_experimental_instance_list
)

# We can also simplify our parameter representation by combining all the relevant experiment instances in the same order as the experiment instances.

rf_vna_calibration_parameters = (
    through_parameters
    + open_parameters_list
    + load_parameters_list
    + short_parameters_list
)

# Now we can create an `Experiment` from this:

rf_vna_self_calibration = pe.types.Experiment(
    name="rf_vna_self_calibration",
    experiment_instances=vna_self_calibration_experiment_instances,
    parameters_list=rf_vna_calibration_parameters,
)

# Let's create the directories in which to save the data accordingly:

experiment_data_directory = piel.return_path("data")
piel.create_new_directory(experiment_data_directory)

# Now, we can create the experiment in there:

vna_self_calibration_experiment_directory = pe.construct_experiment_directories(
    experiment=rf_vna_self_calibration,
    parent_directory=experiment_data_directory,
)

# We can also see the generated table in the `README.md` of the top level experiment:
#
# |    |   port | measurement   | calibration   |
# |---:|-------:|:--------------|:--------------|
# |  0 |     12 | through       | vna_ports     |
# |  1 |      1 | open          | vna_ports     |
# |  2 |      2 | open          | vna_ports     |
# |  3 |      1 | load          | vna_ports     |
# |  4 |      2 | load          | vna_ports     |
# |  5 |      1 | short         | vna_ports     |
# |  6 |      2 | short         | vna_ports     |

# We can now perform our measurements and save the data in this directory, and it saves all the corresponding metadata that we care about alongside it. Once we have done that, we can also extract the corresponding measurements of data already saved in the directory.
#
# We want a functionality that helps us analyse and construct the data into a data structure that makes sense alongside all the metadata. We want to construct the `ExperimentData` from this accordingly. Now, we know that in this `Experiment`, we are mainly using frequency-domain s-parameter data. This enables us to have a set of functions that operate on `Experiment` to automatically create `ExperimentData` with everything ready for us to use internally:

rf_vna_self_calibration_data = pe.extract_data_from_experiment(
    experiment=rf_vna_self_calibration,
    experiment_directory=vna_self_calibration_experiment_directory,
)
rf_vna_self_calibration_data.data.collection

# ```python
# [VNASParameterMeasurementData(name='through_port_12', network=2-Port Network: 'through_port_12',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='open_port_1', network=2-Port Network: 'open_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='open_port_2', network=2-Port Network: 'open_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='load_port_1', network=2-Port Network: 'load_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='load_port_2', network=2-Port Network: 'load_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='short_port_1', network=2-Port Network: 'short_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='short_port_2', network=2-Port Network: 'short_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j])]
# ```

# We could simply skip all of this and extract the data directly from the directory. Note that we don't always have to work from the same python instance as we can reload the classes (with some caveats) from the metadata.

reinstantiated_vna_self_calibration_experiment_data = (
    pe.load_experiment_data_from_directory(
        experiment_directory=vna_self_calibration_experiment_directory,
    )
)
reinstantiated_vna_self_calibration_experiment_data.data.collection

# ```python
# [VNASParameterMeasurementData(name='through_port_12', network=2-Port Network: 'through_port_12',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='open_port_1', network=2-Port Network: 'open_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='open_port_2', network=2-Port Network: 'open_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='load_port_1', network=2-Port Network: 'load_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='load_port_2', network=2-Port Network: 'load_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='short_port_1', network=2-Port Network: 'short_port_1',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j]),
#  VNASParameterMeasurementData(name='short_port_2', network=2-Port Network: 'short_port_2',  45000000.0-20000000000.0 Hz, 6401 pts, z0=[50.+0.j 50.+0.j])]
# ```

# Now, we can begin plotting this data in multiple ways:

# ### A HW Calibrated Open-Measurement
#
# Our two unconnected connection with the calibration applied at the machine might give a measurement such as this one.
#
# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_cal_open.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>


# We can plot this data, for example, still using `scikit-rf` as usual:

stylely()
fig, axs = plt.subplots(2, 1, figsize=(8, 6))
calibrated_vna_port1_open_network = rf_vna_self_calibration_data.data.collection[
    1
].network.subnetwork([0])  # only looking at port 1
calibrated_vna_port1_open_network.plot_s_db(ax=axs[0])
calibrated_vna_port1_open_network.plot_s_deg(ax=axs[1])
axs[0].set_title("Real S11")
axs[1].set_title("Imaginary S11")
plt.tight_layout()
fig.savefig(
    "../../_static/img/examples/08_basic_interconnection_modelling/skrf_plot_open.jpg"
)

# ![skrf_plot_open](../../_static/img/examples/08_basic_interconnection_modelling/skrf_plot_open.jpg)

# This is the same data you should get if you connect the open calibration port from the calibration kit into any of the VNA connection.

# It is important to note we can also map the keys to the data index using the `Experiment` metadata. Normally, it would simply be easier to have keys map to the corresponding `MeasurementData` instance. However, when there are multiple parameters in a given set of measurements, it can be too much to reasonably index. Hence, it is in this case that a parameter index mapping can be useful. We can simply use the `parameters_list` we initially composed for our `Experiment` and `pandas` or whatever else.

rf_vna_self_calibration_data.experiment.parameters

# |    |   port | measurement   | calibration   |
# |---:|-------:|:--------------|:--------------|
# |  0 |     12 | through       | vna_ports     |
# |  1 |      1 | open          | vna_ports     |
# |  2 |      2 | open          | vna_ports     |
# |  3 |      1 | load          | vna_ports     |
# |  4 |      2 | load          | vna_ports     |
# |  5 |      1 | short         | vna_ports     |
# |  6 |      2 | short         | vna_ports     |

# ### A HW Calibrated Short Measurement

# Now, let's connect a short calibration port into one of the VNA connection. You can note that obviously the insertion loss doesn't change as this is just a port to port measurement and should affect mainly the phase.
#
# We can, for example, also use the data directly without having to use any `piel` data structures. This can be useful if you want to use this functionality to create the metadata and directories but not interact with other functionality in the package.
#
# You might, for example, already have a stylesheet for your project and don't want to deviate from this when using `scikit-rf`. This unfortunately requires some tweaking as many of the `scikit-rf` plotting functionality may simply not look nice enough accordingly. You can also activate your styles, in our case `piel.experimental.styles.activate_piel_styles` would activate `piel` styling functionality.

pv.style.activate_piel_styles()
fig, axs = plt.subplots(2, 1, figsize=(10, 6))
calibrated_short_data_file = "data/rf_vna_self_calibration/5/short_port1.s2p"
calibrated_vna_port1_short_network = hfss_touchstone_2_network(
    calibrated_short_data_file
).subnetwork([0])  # Only looking at port1
calibrated_vna_port1_short_network.plot_s_db(ax=axs[0])
calibrated_vna_port1_short_network.plot_s_deg(ax=axs[1])
axs[0].set_title("Real S11")
axs[1].set_title("Imaginary S11")
plt.tight_layout()
fig.savefig(
    "../../_static/img/examples/08_basic_interconnection_modelling/skrf_plot_short.jpg"
)

# ![skrf_plot_open](../../_static/img/examples/08_basic_interconnection_modelling/skrf_plot_short.jpg)

# ### A HW Calibrated Load Measurement

calibrated_load_data_file = "data/rf_vna_self_calibration/3/load_port1.s2p"
calibrated_vna_port1_load_network = hfss_touchstone_2_network(calibrated_load_data_file)
calibrated_vna_port1_load_network.plot_s_db()
plt.tight_layout()

# ### A HW Calibrated Through-Measurement
#
# This measurement is particularly useful for determining the insertion loss through our component. In this case, we should expect zero insertion loss as it is a measurement on the through calibration reference.
#
# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_cal_through.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>

# It might also be desired to plot each of the s-parameter elements in different axes.

fig, axs = pv.create_plot_containers(
    container_list=["PORT1", "PORT2"], axes_per_element=2
)
calibrated_load_data_file = "data/rf_vna_self_calibration/0/through_port1_port2.s2p"
calibrated_vna_port1_load_network = hfss_touchstone_2_network(calibrated_load_data_file)
for m in range(2):
    for n in range(2):
        calibrated_vna_port1_load_network.plot_s_db(ax=axs[m, n], m=m, n=n)
fig.savefig(
    "../../_static/img/examples/08_basic_interconnection_modelling/basic_plot_through.jpg"
)

# ![basic_plot_through](../../_static/img/examples/08_basic_interconnection_modelling/basic_plot_through.jpg)

# You can implement a very similar functionality directly with `piel`. Note that you need to import the corresponding function from the type of data input you want to provide, in order for the function to compile the corresponding inputs and `metadata` from the current location. In this case, it is from a `MeasurementDataCollection`

piel.visual.experimental.frequency.measurement_data_collection.plot_s_parameter_per_component(
    data_collection=reinstantiated_vna_self_calibration_experiment_data.data,
    parameters_list=reinstantiated_vna_self_calibration_experiment_data.experiment.parameters_list,
    s_parameter_plot="plot_s_db",
    path="../../_static/img/examples/08_basic_interconnection_modelling/reinstantiate_subset_example_plot_through.jpg",
)

# ![reinstantiate_subset_example_plot_through](../../_static/img/examples/08_basic_interconnection_modelling/reinstantiate_subset_example_plot_through.jpg)

# #### Further Automatic Plotting Functionality
#
# Now, you might have `MeasurementCollection` or `ExperimentData` with many `s-parameters` data. It might just be easier to get the feel of all of them by automatically plotting them using some of the generic visualisation utilities in `piel` such these. You can also copy the source code through Github and modify your own function from them, and are most welcome to contribute/PR back into the project.

# We might also want to automate a lot of certain measurement of plots. `scikit-rf` already does a great job at this. In our case, we might want to give our plotting functions a set of `ExperimentalData` measurement collections with a given set of networks and metadata and be able to easily plot this according to the type of plot structure we want. `piel` provide a common set of examples that can help automate some of this for some functionality.

# **Plotting from the ExperimentData**
#
# For example, you can simply plot directly from a provided `ExperimentData` accordingly too.

# + active=""
# piel.visual.experimental.frequency.experiment_data.plot_s_parameter_real_and_imaginary(
#     rf_vna_self_calibration_data,
#     path="../../_static/img/examples/08_basic_interconnection_modelling/s_parameter_re_im_vna_calibration_experiment_data_collection.jpg",
# )
# -


# **Creating Reports**

# We can also create a set of automatic plots directly from the `ExperimentData` and create a `REPORT.md` on the experiment directory.

# +
# report_info = pe.create_report_from_experiment_directory(
#     experiment_directory=vna_self_calibration_experiment_directory,
# )
# -

# ```
# Experiment data will be extracted from: /home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/data/rf_vna_self_calibration
# Plots will be generated at: /home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/data/rf_vna_self_calibration/img
# Figure saved at: /home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/data/rf_vna_self_calibration/img/None_plot_s_parameter_real_and_imaginary.png
# README.md updated at: /home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/data/rf_vna_self_calibration/README.md
# REPORT.md written to: /home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/data/rf_vna_self_calibration/REPORT.md
# ```

# We can also create a parametric plot with automatically analyzed operation points accordingly.

# +
# # This takes a while to run, uncomment if interested
# report_info = pe.create_report_from_experiment_directory(
#     experiment_directory=vna_self_calibration_experiment_directory,
#     plot_kwargs={"parametric": True},
# )
# -

# **Plotting from Operating Points**
#
# We might also want to extract the relevant operating points from a given `ExperimentData` in order to create an `ExperimentDataCollection`. We can automate the creation of the corresponding `ExperimentData` subsets based on the operating points in the `Experiment.parameters_list`.

# + active=""
# example_subset_data_collection = (
#     pe.create_experiment_data_collection_from_unique_parameters(
#         experiment_data=rf_vna_self_calibration_data
#     )
# )
# # TODO show this works example_subset_data_collection
# -

# #### Identifying bad/shifting calibration

# We identified we had another damaged calibration kit due to the way the reference plots were generated.
#
# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_bad_cal_terminator.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>

measured_badly_calibrated_terminator_data_file = (
    "measurement_data/badly_calibrated_terminator.s2p"
)
badly_calibrated_terminator_network = hfss_touchstone_2_network(
    measured_badly_calibrated_terminator_data_file
)
badly_calibrated_terminator_network.plot_s_db()

# ### Software De-embedding implementations & Verification

# #### Why inverse-matrix-multipling measurement extraction does not work practically?
#
# There are cases in which we might want to de-embed a measurement from another measurement. This has to do with moving the reference planes between two measurements. Say, with a given calibration, we perform a through measurement of two cables and another through measurements of three cables, two which were in the first measurement. It would be nice if we could determine the performance of the third new cable in the two cable network without having to recalibrate to the two-original-cables reference plane. This is the type of situation this comes handy.
#
# This is not exactly "de-embedding" in the hardware-sense of the work, but maybe means more towards software network extraction from measurements.
#
# Now, we will explore how to do this in software and verify this experimentally.
#
# TODO make diagram.
#
# In order to demonstrate this, we will start from a through-measurement of two cables as above with just the VNA port calibration applied.

calvna_cables_through_data_file = (
    "measurement_data/software_deembedding/inverse_multiply/calvna_cables_through.s2p"
)
calvna_cables_through_network = hfss_touchstone_2_network(
    calvna_cables_through_data_file
)
calvna_cables_through_network.plot_s_db()

# Now, we can measure how the same measurement with a `20dB` 2081-6148-20 attenuator used to model a lossy cable would be.

calvna_cables_20db_attenuator_data_file = "measurement_data/software_deembedding/inverse_multiply/calvna_cables_20db_attenuator_2082614820.s2p"
calvna_cables_20db_attenuator_network = hfss_touchstone_2_network(
    calvna_cables_20db_attenuator_data_file
)
calvna_cables_20db_attenuator_network.plot_s_db()

# Note that we can also de-embed a network with itself, and the result should be unitary or near-zero transmission depending on the port.

self_dembedded_network = skrf.network.de_embed(
    calvna_cables_through_network, calvna_cables_through_network
)
self_dembedded_network.plot_s_db()

# Note that if the measurements are not approximately similar in terms of the magnitude of the responses, say because one SMA has been screwed tighter than in another measurement, then this type of network measurement de-embedding is inaccurate. This can be observed in the image below:

software_dembeded_attenuator = skrf.network.de_embed(
    calvna_cables_through_network, calvna_cables_20db_attenuator_network
)
software_dembeded_attenuator.plot_s_db()


# #### Configuring a software calibration scheme

# `scikit-rf` have other ways to perform calibration and de-embedding.
#
# Some relevant examples and references are:
#
# * https://scikit-rf.readthedocs.io/en/latest/examples/metrology/SOLT.html
# * https://scikit-rf.readthedocs.io/en/latest/api/calibration/deembedding.html
# * https://scikit-rf.readthedocs.io/en/latest/api/calibration/index.html
#
# We can use given measurements from one HW calibration protocol to perform a software calibration protocol we can use to correct our measurements.

# First, let's create our reference measurements. Note that the way the data was saved was a bit raw format, so let's first construct this into a data format that is easily integrateable with the functionality we want to achieve.


def construct_calibration_networks(measurements_directory: piel.PathTypes):
    """
    This function takes a directory with a collection of ``.s2p`` measurements and constructs the relevant calibration measurements accordingly.
    In this case, this function is meant to filter out files which follow the following directory structure.
    Ideally it would have been better to save individual signals as ``.s1p`` files but it can be easier sometimes to save as `.s2p` files.

    .. raw::

        load_port1.s2p
        open_port1.s2p
        short_port1.s2p
        through_port1_port2.s2p
        load_port2.s2p
        open_port2.s2p
        short_port2.s2p

    In this sense, we provide a given directory with these files, and this function extracts the relevant measurements accordingly.
    """
    directory = piel.return_path(measurements_directory)

    # Configure our data containers
    files = os.listdir(directory)
    raw_networks = {}
    networks = {}

    one_port_references = ["short", "open", "load"]
    for one_port_reference_name in one_port_references:
        raw_networks[one_port_reference_name] = dict()
        networks[one_port_reference_name] = None

    # Now we iterate on this directory to list all the files
    for file in files:
        # TODO possibly do the .s1p files here.
        if file.endswith(".s2p"):
            # Construct the relevant file names
            file_name = directory / file

            # Filter for .s2p files according to relevant measrurements
            if "through" in file:
                through_network = hfss_touchstone_2_network(file_name)
                raw_networks["through"] = through_network
                networks["through"] = through_network

            for one_port_reference_name_i in one_port_references:
                if one_port_reference_name_i in file:
                    if "port1" in file:
                        raw_networks[one_port_reference_name_i][1] = (
                            hfss_touchstone_2_network(file_name)
                        )
                    elif "port2" in file:
                        raw_networks[one_port_reference_name_i][2] = (
                            hfss_touchstone_2_network(file_name)
                        )

    # Now we need to construct the relevant reciprocal networks from a collection of two-port networks
    for one_port_reference_name_i in one_port_references:
        for port_i, two_port_network_i in raw_networks[
            one_port_reference_name_i
        ].items():
            if port_i == 1:
                port_1_network = skrf.subnetwork(
                    two_port_network_i, [port_i - 1]
                )  # 1 port Network from ports_i
            if port_i == 2:
                port_2_network = skrf.subnetwork(
                    two_port_network_i, [port_i - 1]
                )  # 1 port Network from ports_i

        # Combine them together
        networks[one_port_reference_name_i] = skrf.two_port_reflect(
            port_1_network, port_2_network
        )

    return networks


# +
a = construct_calibration_networks(
    measurements_directory="./measurement_data/calibration_kit_vna_cal_at_vna_ports/"
)

b = construct_calibration_networks(
    measurements_directory="./measurement_data/calibration_kit_vna_cal_at_cable_ports"
)

# -


ideal = [i for i in a.values()]
measured = [i for i in b.values()]

cal = skrf.calibration.SOLT(
    ideals=ideal,
    measured=measured,
)


# +
cal.run()

piel.visual.activate_piel_styles()
fig, axs = piel.visual.create_axes_per_figure(1, 3, figsize=(12, 4))


# apply it to a dut
dut = skrf.Network(
    "./measurement_data/calibration_kit_vna_cal_at_cable_ports/attenuator_20db.s2p"
)
dut_caled = cal.apply_cal(dut)
hw_caled = hfss_touchstone_2_network(
    "/home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/measurement_data/calibration_kit_vna_cal_at_vna_ports/attenuator_20db.s2p"
)

# plot results
dut.plot_s_db(ax=axs[0], title="SOLT Software Uncalibrated")
dut_caled.plot_s_db(ax=axs[1], title="SOLT Software Calibrated")
hw_caled.plot_s_db(ax=axs[2], title="SOLT Hardware Calibrated")

fig.savefig(
    "../../_static/img/examples/08_basic_interconnection_modelling/solt_calibration_example.jpg"
)
# -

# ![solt_calibration_example](../../_static/img/examples/08_basic_interconnection_modelling/solt_calibration_example.jpg)

# +
piel.visual.activate_piel_styles()
fig, axs = piel.visual.create_axes_per_figure(1, 3, figsize=(12, 4))


# apply it to a dut
dut = skrf.Network(
    "./measurement_data/calibration_kit_vna_cal_at_cable_ports/attenuator_20db.s2p"
)
dut_caled = cal.apply_cal(dut)
hw_caled = hfss_touchstone_2_network(
    "/home/daquintero/phd/piel/docs/examples/08_basic_interconnection_modelling/measurement_data/calibration_kit_vna_cal_at_vna_ports/attenuator_20db.s2p"
)

dut = piel.integration.convert_to_network_transmission(dut)
dut_caled = piel.integration.convert_to_network_transmission(dut_caled)
hw_caled = piel.integration.convert_to_network_transmission(hw_caled)

# plot results
piel.visual.plot.signals.frequency.plot_s11_s21_magnitude_per_input_frequency(
    dut,
    fig,
    [axs[0]],
    title="SOLT Software Uncalibrated",
)

piel.visual.plot.signals.frequency.plot_s11_s21_magnitude_per_input_frequency(
    dut_caled,
    fig,
    [axs[1]],
    title="SOLT Software Calibrated",
    ylabel="",
)

piel.visual.plot.signals.frequency.plot_s11_s21_magnitude_per_input_frequency(
    hw_caled,
    fig,
    [axs[2]],
    title="SOLT Hardware Calibrated",
    ylabel="",
)

ylimit = [-50, 10]
axs[0].set_ylim(ylimit)
axs[1].set_ylim(ylimit)
axs[2].set_ylim(ylimit)

fig.savefig(
    "../../_static/img/examples/08_basic_interconnection_modelling/solt_calibration_example_piel.jpg"
)
# -

# ![solt_calibration_example_piel](../../_static/img/examples/08_basic_interconnection_modelling/solt_calibration_example_piel.jpg)

# #### Comparison with Hardware De-Embedding
#
# So this means that the hardware calibration seems to provide less noisy results than performing the sfotware calibration. However, the software calibration seems to be more "correct" than the uncalibrated measurements and as such, probably provides more understanding of the actual operation within these measurements.
#
# Say, for the same calibration as the measurements above, we can now measure just the attenuator and compare with the de-embedded reference.

# We can compare these software calibrations with the equivalent hardware calibrations in this Figure.

# We can now verify this measurement with the hardware-deembedding up to those two cables.

calvna_20db_attenuator_data_file = "measurement_data/software_deembedding/inverse_multiply/calvna_20db_attenuator_2082614820.s2p"
calvna_20db_attenuator_network = hfss_touchstone_2_network(
    calvna_20db_attenuator_data_file
)
calvna_20db_attenuator_network.plot_s_db()

# ### Measurement Verification of a Coaxial-Cable

# A coaxial cable is a transmission line, which means it has a signal transmission associated with it for a range of RF frequencies. We might want to explore how the attenuation and reflection of our high-frequency signals operate. Let's understand some network theory basics in relation to an actual measurement context.
#
# In this example, we will consider the measurement PNA network measurement of a [141-1MSM+](https://www.minicircuits.com/WebStore/dashboard.html?model=141-1MSM%2B) cable and compare it to some network theory.
#
# Note that it is important to know the fundamental limits of the measurement. For example, for an SMA 3.5mm network, the bandwidth is inherently limited to 18-24.5 GHz.

# This are some performance metrics of this cable as described by the [datasheet](https://www.minicircuits.com/pdfs/141-1MSM+.pdf):
#
# ![rf_plots_1411MSM](../../_static/img/examples/08_basic_interconnection_modelling/rf_plots_1411MSM.png)

# +

# 141-1MSM+ cable datasheet model
data = {
    "frequency_mhz": [
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
        900.0,
        1000.0,
        1100.0,
        1250.0,
        1500.0,
        1750.0,
        2000.0,
        2250.0,
        2500.0,
        2750.0,
        3000.0,
        3250.0,
        3500.0,
        3750.0,
        4000.0,
        4250.0,
        4500.0,
        5000.0,
        5500.0,
        6000.0,
        6500.0,
        7000.0,
        7500.0,
        8000.0,
        8500.0,
        9000.0,
        9500.0,
        10000.0,
        11000.0,
        12000.0,
        13000.0,
        13500.0,
        14000.0,
        14500.0,
        15000.0,
        15500.0,
        16000.0,
        16500.0,
        17000.0,
        17500.0,
        18000.0,
    ],
    "insertion_loss_db": [
        0.12,
        0.18,
        0.21,
        0.26,
        0.28,
        0.31,
        0.34,
        0.40,
        0.43,
        0.46,
        0.44,
        0.47,
        0.52,
        0.55,
        0.62,
        0.63,
        0.66,
        0.70,
        0.74,
        0.77,
        0.80,
        0.84,
        0.87,
        0.90,
        0.93,
        0.99,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25,
        1.30,
        1.35,
        1.40,
        1.45,
        1.49,
        1.58,
        1.67,
        1.75,
        1.81,
        1.85,
        1.90,
        1.92,
        1.97,
        2.04,
        2.07,
        2.11,
        2.16,
        2.21,
    ],
    "return_loss_db_male1": [
        44.6,
        40.1,
        36.7,
        33.9,
        33.5,
        32.4,
        31.9,
        30.3,
        30.2,
        31.8,
        35.7,
        31.2,
        37.7,
        36.0,
        33.3,
        48.7,
        42.0,
        40.5,
        43.9,
        37.1,
        40.4,
        47.1,
        41.5,
        35.4,
        40.2,
        36.4,
        38.5,
        35.8,
        40.9,
        37.6,
        38.4,
        35.8,
        31.9,
        45.3,
        30.5,
        42.2,
        35.1,
        28.1,
        34.3,
        25.3,
        24.8,
        26.5,
        30.2,
        26.0,
        23.6,
        27.6,
        23.5,
        23.2,
        21.8,
    ],
    "return_loss_db_male2": [
        53.6,
        46.1,
        42.2,
        38.3,
        37.6,
        36.7,
        36.3,
        35.9,
        35.4,
        35.3,
        37.5,
        36.5,
        55.5,
        38.2,
        38.0,
        46.6,
        44.2,
        43.1,
        46.5,
        38.1,
        48.5,
        45.0,
        39.7,
        43.6,
        40.4,
        39.7,
        36.3,
        34.5,
        41.2,
        39.1,
        36.8,
        34.1,
        31.5,
        37.3,
        28.3,
        42.3,
        36.8,
        29.2,
        43.9,
        29.3,
        25.9,
        23.5,
        32.7,
        27.2,
        22.4,
        25.8,
        23.6,
        22.7,
        22.5,
    ],
}


# Create a DataFrame
df = pd.DataFrame(data)
plt.plot(df.frequency_mhz, -df.insertion_loss_db)
plt.plot(df.frequency_mhz, -df.return_loss_db_male1)
# -

# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_coax.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>
#
#
#

measured_mid_resolution_14111msm_data_file = "measurement_data/mid_res_1411msm_cal1.s2p"
mid_resolution_14111msm_network = hfss_touchstone_2_network(
    measured_mid_resolution_14111msm_data_file
)
mid_resolution_14111msm_network

mid_resolution_14111msm_network.plot_s_db()

measured_high_resolution_14111msm_data_file = (
    "measurement_data/high_res_1411msm_cal1.s2p"
)
high_resolution_14111msm_network = hfss_touchstone_2_network(
    measured_high_resolution_14111msm_data_file
)
high_resolution_14111msm_network

high_resolution_14111msm_network.plot_s_db()

# ###  Post-Calibration Frequency-Domain Measurement

calibrated_14111msm_data_file = "measurement_data/1411msm_cal2.s2p"
calibrated_14111msm_network = hfss_touchstone_2_network(calibrated_14111msm_data_file)
calibrated_14111msm_network

calibrated_14111msm_network.plot_s_db()

748 * (((31 - 22) + (14)) / 30)

748 * (20 / 31)

# ## Understanding S-Parameter Power Sweeps

measured_high_resolution_14111msm_data_file = "measurement_data/example_power_sweep.s2p"
high_resolution_14111msm_network = skrf.Network(
    measured_high_resolution_14111msm_data_file
)
high_resolution_14111msm_network
