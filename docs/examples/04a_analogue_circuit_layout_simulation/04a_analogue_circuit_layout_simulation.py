# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Analogue Circuit Layout & Simulation

# ## Virtuoso Data Extraction

# You might already have a design in Cadence Virtuoso but might want to export some simulation data to use it in a larger co-design flow. `piel` provides limited import functionality currently.


# # Open-Source Flow
#
# ## Going through the Basics

# We will start off by importing the layout elements of the SKY130nm `gdsfactory` PDK process and understanding how we interact and map them to a schematic.

# TODO MOVE TO DOCUMENTATION WHEN MORE ADVANCED.
#
# One thing that many people might want to do is design analog circuits on chip using open-source tools.`gdsfactory` is an excellent tool for chip  layout. `hdl21` and `vlsir` are great projects to perform simulation in most open-source and proprietary SPICE simulation platforms. It makes sense to integrate the two together. We will demonstrate how to do this in this example.
#
# A collection of Google-released open-source PDKs is available [here](https://foss-eda-tools.googlesource.com/)
#
# There are several open-source PDKs. At the moment some of the most popular ones are:
#
# **SKY130nm**
# -  [Main Open-ScalarSource Release](https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hd/tree/ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1)
# -  [`gdsfactory` layout PDK integration](https://github.com/gdsfactory/skywater130)
# -  [`hdl21` integration](https://github.com/dan-fritchman/Hdl21/tree/main/pdks/Sky130)
#
# **GF180nm**
# -  [Main Open-ScalarSource Release](https://github.com/google/gf180mcu-pdk)
#
# **IHP130nm**
# -  [Main Open-ScalarSource Release](https://github.com/IHP-GmbH/IHP-Open-PDK)
#
# **Any PDK**
# -  [`gdsfactory` import instructions](https://gdsfactory.github.io/gdsfactory/notebooks/09_pdk_import.html)
# -  [`hdl21` instructions](https://github.com/dan-fritchman/Hdl21/tree/main/pdks/PdkTemplate)
#
# So, as we can see, there currently are many separate relevant projects that solve different aspects of an integration flow. What we would like to do is to have an integrated flow where we could, for example, do some schematic-driven-layout or some layout-driven-schematic extraction. These are some of the objectives of the flow that we would like to demonstrate.

# ## Starting from an Op-Amp Model

# ## Using the `gdsfactory-sky130nm` Repository

# The goal of this notebook is to show that analogue simulation and layout can be performed together within a `gdsfactory` environment.

# +
import hdl21 as h
import gdsfactory as gf
import piel
import sky130_hdl21

from bokeh.io import output_notebook

gf.config.rich_output()

# %env BOKEH_ALLOW_WS_ORIGIN=*

output_notebook()


# +
# sky130.cells
# sky130.cells["sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield"]()
# -


@h.module
class SkyInv:
    """An inverter, demonstrating using PDK modules"""

    # Create some IO
    i, o, VDD, VSS = h.Ports(4)

    p = sky130_hdl21.Sky130MosParams(w=1, l=1)

    # And create some transistors!
    ps = sky130_hdl21.primitives.PMOS_1p8V_STD(p)(d=o, g=i, s=VDD, b=VDD)
    ns = sky130_hdl21.primitives.NMOS_1p8V_STD(p)(d=VSS, g=i, s=o, b=VSS)


# ### Schematic-Driven-Layout
#
# A common analogue design flow is called schematic-driven-layout. What this entails, fundamentally, is that we design a circuit through a schematic, and then use that schematic to instruct, extract, constrain, and/or verify our circuit chip layout. This flow uses layout elements that are connected or tied to schematic symbols, and unique names that allow for identification and connectivity relationship.
#
# -  You can read [how this is done in Cadence](https://web.njit.edu/~tyson/cadence%20Layout_Tutorial.pdf)
#
# In an open-source flow, this could be, for example, demonstrated by creating a circuit using the `hdl21 schematic` tools. Each symbol would reference a specific `PCell` in the PDK. Now, we would use this individual element cell name to connect and extract to the `SPICE` model and also to the `layout` GDS cell. This allows us to connect to the separate tools for simulation and layout.
#
# Say, we can then extract a netlist from the schematic with individual cell names and PDK cells identifiers. We could in `gdsfactory` map these PDK cell identifiers to instantiate the elements in a layout. We can then use this instantated cells to perform some automatic or
#
# It is important to know that with the SPICE-generated YAML, we cannot actually create a layout on its own. This is because the SPICE measurement do not exactly directly map to layout instances. SPICE measurement can represent performance corners for the same device, with multiple temperature or yield quality variations. As such, we need to assign the corresponding gds we want to layout for our specific schematic model.

example_inverter_manual_yaml = piel.integration.generate_raw_yaml_from_module(SkyInv)
print(example_inverter_manual_yaml)

example_inverter_manual_yaml = """
connections:
  ns,d: ps,d
  ns,g: ps,g
  ps,d: ns,d
  ps,g: ns,g
instances:
  ns:
    component: sky130_fd_pr__nfet_01v8
    info: {}
    settings:
      As: int((nf+2)/2) * w/nf * 0.29
      ad: int((nf+1)/2) * w/nf * 0.29
      l: UNIT_1
      m: UNIT_1
      mult: UNIT_1
      nf: UNIT_1
      nrd: 0.29 / w
      nrs: 0.29 / w
      pd: 2*int((nf+1)/2) * (w/nf + 0.29)
      connection:
        b: VSS
        d: o
        g: i
        s: VSS
      ps: 2*int((nf+2)/2) * (w/nf + 0.29)
      sa: UNIT_0
      sb: UNIT_0
      sd: UNIT_0
      w: UNIT_1
  ps:
    component: sky130_fd_pr__pfet_01v8
    info: {}
    settings:
      As: int((nf+2)/2) * w/nf * 0.29
      ad: int((nf+1)/2) * w/nf * 0.29
      l: UNIT_1
      m: UNIT_1
      mult: UNIT_1
      nf: UNIT_1
      nrd: 0.29 / w
      nrs: 0.29 / w
      pd: 2*int((nf+1)/2) * (w/nf + 0.29)
      connection:
        b: VDD
        d: o
        g: i
        s: VDD
      ps: 2*int((nf+2)/2) * (w/nf + 0.29)
      sa: UNIT_0
      sb: UNIT_0
      sd: UNIT_0
      w: UNIT_1
name: SkyInv
connection:
  VDD: ps,s
  VSS: ns,s
  i: ps,g
  o: ps,d
"""
with open("example_inverter_manual.schem.yaml", "w") as file:
    file.write(example_inverter_manual_yaml)

# ### Automatically mapping layout instances to the YAML - Inverter

example_inverter_schematic_editor = piel.integration.hdl21_module_to_schematic_editor(
    module=SkyInv,
    yaml_schematic_file_name="example_inverter_auto.schem.yaml",
)
example_inverter_schematic_editor.visualize()

example_inverter_layout = "example_inverter_auto.layout.yaml"
example_inverter_schematic_editor.instantiate_layout(
    example_inverter_layout,
    default_router="get_bundle",
    default_cross_section="xs_metal1",
)
c = gf.read.from_yaml(example_inverter_layout)
c.plot()

# ### More Advanced Example - R2R DAC
#
#
# An example of using `hdl21.ExternalModule`s representing an implementation technology/ PDK
# in a parametric resistive DAC generator mapping to a gdsfactory implementation.

# +
from typing import Optional

import hdl21 as h

PdkResistor = sky130_hdl21.ress["GEN_PO"]
Nch = sky130_hdl21.primitives.NMOS_1p8V_STD
Pch = sky130_hdl21.primitives.PMOS_1p8V_STD


@h.paramclass
class RLadderParams:
    """# Resistor Ladder Parameters

    Note the use of the `hdl21.Instantiable` type for the unit resistor element.
    This generally means "something we can make an `Instance` of" - most commonly a `Module`.

    Here we will be using a combination of an `ExternalModule` and its parameter-values,
    in something like:

    ```python
    RLadderParams(res=PdkResistor(w=4 * µ, l=10 * µ))
    ```
    """

    nseg = h.Param(dtype=int, desc="Number of segments")
    res = h.Param(dtype=h.Instantiable, desc="Unit resistor, with params applied")


@h.generator
def rladder(params: RLadderParams) -> h.Module:
    """# Resistor Ladder Generator"""

    @h.module
    class RLadder:
        # IO
        top = h.Inout()
        bot = h.Inout()
        taps = h.Output(width=params.nseg - 1)

        # Create concatenations for the P and N sides of each resistor
        nsides = h.Concat(bot, taps)
        psides = h.Concat(taps, top)

        # And create our unit resistor array
        runits = params.nseg * params.res(p=psides, n=nsides)

    return RLadder


@h.paramclass
class PassGateParams:
    """# Pass Gate Parameters

    See the commentary on `RLadderParams` above regarding the use of `hdl21.Instantiable`,
    which here serves as the parameter type for each transistor. It will generally be used like:

    ```python
    PassGateParams(
        nmos=Nch(PdkMosParams(l=1 * n)),
        pmos=Pch(PdkMosParams(l=1 * n)),
    )
    ```

    Both `nmos` and `pmos` parameters are `Optional`, which means they can be set to the Python built-in `None` value.
    If either is `None`, its "half" of the pass gate will be omitted.
    Setting *both* to `None` will cause a gPASSenerator exception.
    """

    nmos = h.Param(dtype=Optional[h.Instantiable], desc="NMOS. Disabled if None.")
    pmos = h.Param(dtype=Optional[h.Instantiable], desc="PMOS. Disabled if None")


@h.generator
def passgate(params: PassGateParams) -> h.Module:
    """# Pass Gate Generator"""
    if params.nmos is None and params.pmos is None:
        raise RuntimeError("A pass gate needs at least *one* transistor!")

    @h.module
    class PassGate:
        source = h.Inout()
        drain = h.Inout()

    if params.pmos is not None:
        PassGate.VDD = h.Inout()
        PassGate.en_b = h.Input()
        PassGate.PSW = params.pmos(
            d=PassGate.drain, s=PassGate.source, g=PassGate.en_b, b=PassGate.VDD
        )

    if params.nmos is not None:
        PassGate.VSS = h.Inout()
        PassGate.en = h.Input()
        PassGate.NSW = params.nmos(
            d=PassGate.drain, s=PassGate.source, g=PassGate.en, b=PassGate.VSS
        )

    return PassGate


@h.generator
def mux(params: PassGateParams) -> h.Module:
    """# Pass-Gate Analog Mux Generator"""

    @h.module
    class Mux:
        sourceA = h.Input()
        sourceB = h.Input()
        out = h.Output()
        ctrl = h.Input()
        ctrl_b = h.Input()

    aconns, bconns = (
        dict(source=Mux.sourceA, drain=Mux.out),
        dict(source=Mux.sourceB, drain=Mux.out),
    )
    if params.pmos is not None:
        Mux.VDD = h.Inout()
        aconns["VDD"] = Mux.VDD
        aconns["en_b"] = Mux.ctrl_b
        bconns["VDD"] = Mux.VDD
        bconns["en_b"] = Mux.ctrl
    if params.nmos is not None:
        Mux.VSS = h.Inout()
        aconns["VSS"] = Mux.VSS
        aconns["en"] = Mux.ctrl
        bconns["VSS"] = Mux.VSS
        bconns["en"] = Mux.ctrl_b
    Mux.passgate_a = passgate(params)(**aconns)
    Mux.passgate_b = passgate(params)(**bconns)
    return Mux


@h.paramclass
class MuxTreeParams:
    """# Mux Tree Parameters"""

    nbit = h.Param(dtype=int, desc="Number of bits")
    mux_params = h.Param(dtype=PassGateParams, desc="Parameters for the MUX generator")


@h.generator
def mux_tree(params: MuxTreeParams) -> h.Module:
    """Binary Mux Tree Generator"""

    n_inputs = 2**params.nbit
    p_ctrl = params.mux_params.nmos is not None
    n_ctrl = params.mux_params.pmos is not None

    # Base module
    @h.module
    class MuxTree:
        out = h.Output()
        v_in = h.Input(width=n_inputs)
        ctrl = h.Input(width=params.nbit)
        ctrl_b = h.Input(width=params.nbit)

    base_mux_conns = dict()
    if p_ctrl:
        MuxTree.VSS = h.Inout()
        base_mux_conns["VSS"] = MuxTree.VSS
    if n_ctrl:
        MuxTree.VDD = h.Inout()
        base_mux_conns["VDD"] = MuxTree.VDD

    # Build the MUX tree layer by layer
    curr_input = MuxTree.v_in
    for layer in range(params.nbit - 1, -1, -1):
        layer_mux_conns = base_mux_conns.copy()
        layer_mux_conns["ctrl"] = MuxTree.ctrl[layer]
        layer_mux_conns["ctrl_b"] = MuxTree.ctrl_b[layer]
        if layer != 0:
            curr_output = MuxTree.add(name=f"sig_{layer}", val=h.Signal(width=2**layer))
        else:
            curr_output = MuxTree.out
        for mux_idx in range(2**layer):
            mux_conns = layer_mux_conns.copy()
            mux_conns["sourceA"] = curr_input[2 * mux_idx]
            mux_conns["sourceB"] = curr_input[2 * mux_idx + 1]
            mux_conns["out"] = curr_output[mux_idx]
            MuxTree.add(
                name=f"mux_{layer}_{mux_idx}", val=mux(params.mux_params)(**mux_conns)
            )
        curr_input = curr_output
    return MuxTree


"""Main function, generating an `rladder` and `mux_tree` and netlisting each."""

# Create parameter values for each of our top-level generators
rparams = RLadderParams(
    nseg=15,
    res=PdkResistor(),
)
mparams = MuxTreeParams(
    nbit=4,
    mux_params=PassGateParams(
        nmos=Nch(),
        pmos=Pch(),
    ),
)

# Netlist in a handful of formats
duts = [rladder(rparams), mux_tree(mparams)]
# h.netlist(duts, sys.stdout, fmt="verilog")
# h.netlist(duts, sys.stdout, fmt="spectre")
# h.netlist(duts, sys.stdout, fmt="spice")
# h.netlist(duts, sys.stdout, fmt="xyce")
# -

example_resistor_ladder_schematic_editor = (
    piel.integration.hdl21_module_to_schematic_editor(
        module=rladder(rparams),
        yaml_schematic_file_name="rladder.schem.yaml",
    )
)
example_resistor_ladder_schematic_editor.visualize()

example_resistor_ladder_layout_file = "rladder.layout.yaml"
example_inverter_schematic_editor.instantiate_layout(
    example_resistor_ladder_layout_file,
    default_router="get_bundle",
    default_cross_section="xs_metal1",
)
c = gf.read.from_yaml(example_resistor_ladder_layout_file)
c.plot()
