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

# # Electro-Optic Mach-Zehnder Modulator Design & Analysis
#
# The goal of this example is to explore some of the physics related to both the optical and electronic modelling of mach-zehnder modulators. We will demonstrate how the theory matches some of the numerical implementations used throughout `piel`. We will explore device metrics analysis and also show how this can be used in larger system architecture through `piel`.
#
# The main references of this notebook are:
#
# - [1] [*Design, Analysis, and Performance of a Silicon Photonic Travelling Wave Mach-Zehnder Optical Modulator*](https://escholarship.mcgill.ca/downloads/th83m243d?locale=en) by David Patel.
# - [2] Silicon Photonics Design: From Devices to Systems by Lukas Chrostowski and Michael Hochberg

# +
import matplotlib.pyplot as plt
from matplotlib import cm

import piel.models.frequency.photonic
import numpy as np
import jax.numpy as jnp
import pandas as pd
# -

# ## Coupler Modelling
#
# A coupler represents a multi-port connection of optical connection towards another subset of optical connection. They can have many physical implementations, such as directional couplers, multi-mode interference couplers (MMIs), permittivity grid couplers such as those inverse designed, etc.
#
# ### 1x2 Coupler
# A 1x2 coupler, also known as a Y-branch, routes two optical connection into one, or viceversa as this is a reversible linear component. Note that we represent the electric fields as $E_{f}$ as phasors equivalent to $E=Ae^{j\omega + \phi}$. The transfer-matrix model for this device without considering propagation loss is:
#
# \begin{equation}
# \begin{bmatrix}
# E_{Y,o2} \\
# E_{Y,o3}
# \end{bmatrix} =
# \begin{bmatrix}
# \sqrt{\eta_1} \\
# \sqrt{\eta_2}
# \end{bmatrix} E_{o1}
# \end{equation}
#
# Assuming that all the power from the input port is conserved to the two output connection, then the transfer matrix can be written as:
#
# \begin{equation}
# \begin{bmatrix}
# E_{Y,o2} \\
# E_{Y,o3}
# \end{bmatrix} =
# \begin{bmatrix}
# \sqrt{\eta_1} \\
# \sqrt{1-\eta_1}
# \end{bmatrix} E_{o1}
# \end{equation}
#
# An implementation of this coupler in an integrated photonics platform using `gdsfactory` is shown in the image below. Note that the equation notation above matches that within the `gds` implementation:

from gdsfactory.components import mmi1x2

mmi1x2().plot()

# ![mmi_1x2](../_static/img/examples/06a_analytical_mzm_model/mmi_1x2.png)

# The numerical implementation of this transfer matrix in `sax` is, for a 50:50 splitter is:

piel.models.frequency.photonic.mmi1x2_50_50()

# ```python
# {('o1', 'o2'): 0.7071067811865476,
#  ('o1', 'o3'): 0.7071067811865476,
#  ('o2', 'o1'): 0.7071067811865476,
#  ('o3', 'o1'): 0.7071067811865476}
# ```

mmi1x2_transfer_matrix = piel.tools.sax.sax_to_s_parameters_standard_matrix(
    piel.models.frequency.photonic.mmi1x2_50_50(),
    input_ports_order=("o1",),
)
mmi1x2_transfer_matrix

piel.models.frequency.photonic.mmi1x2(splitting_ratio=0.4)

# ```python
# {('o1', 'o2'): 0.6324555320336759,
#  ('o1', 'o3'): 0.7745966692414834,
#  ('o2', 'o1'): 0.6324555320336759,
#  ('o3', 'o1'): 0.7745966692414834}
# ```

# Note that $\sqrt{0.4}$ is:

0.4**0.5

# ### 2x2 Coupler

# \begin{equation}
# \begin{bmatrix}
# E_{o3} \\
# E_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# \sqrt{1 - \eta} & j\sqrt{\eta} \\
# j\sqrt{\eta} & \sqrt{1 - \eta}
# \end{bmatrix}
# \begin{bmatrix}
# E_{o2}\\
# E_{01}
# \end{bmatrix}
# \end{equation}
#
# Note that the imaginary $j$ term causes a $\pi / 2$ phase shift between teh direct and cross coupled inputs

from gdsfactory.components import mmi2x2

mmi2x2().ports

# ![mmi_2x2](../_static/img/examples/06a_analytical_mzm_model/mmi_2x2.png)

mmi2x2_transfer_matrix = piel.tools.sax.sax_to_s_parameters_standard_matrix(
    piel.models.frequency.photonic.mmi2x2(splitting_ratio=0.5),
    input_ports_order=("o2", "o1"),
)
mmi2x2_transfer_matrix

# ```python
# (Array([[0.70710677+0.j        , 0.        +0.70710677j],
#         [0.        +0.70710677j, 0.70710677+0.j        ]], dtype=complex64),
#  ('o2', 'o1'))
# ```

piel.tools.sax.sax_to_s_parameters_standard_matrix(
    piel.models.frequency.photonic.mmi2x2(splitting_ratio=0.4),
    input_ports_order=("o2", "o1"),
)

# ```python
# (Array([[0.7745967+0.j       , 0.       +0.6324555j],
#         [0.       +0.6324555j, 0.7745967+0.j       ]], dtype=complex64),
#  ('o2', 'o1'))
# ```

# We can easily test the logical propagation of a signal:

# Note that this is the absolute amplitude of the signal transmitted through that network.

top_optical_input = jnp.array([[1], [0]])
transmission_amplitude = jnp.abs(jnp.dot(mmi2x2_transfer_matrix[0], top_optical_input))
transmission_amplitude

# ```python
# Array([[0.70710677],
#        [0.70710677]], dtype=float32)
# ```

# We can compute the intensity in both linear and logarithmic units:
#
# In Watts:
#
# \begin{equation}
# I_{W} = |E|^2
# \end{equation}
#
#
# TODO reference base reference of db or dbm?
# \begin{equation}
# I_{dB} = 10 log_{10}(|E|^2)
# \end{equation}

# Hence, we can see that the power is split 50:50 :

transmission_intensity_W = transmission_amplitude**2
transmission_intensity_W

# ```python
# Array([[0.49999997],
#        [0.49999997]], dtype=float32)
# ```

# Or, we can see that each port is $-3dB$ the initial input port, which also matches a 50:50 split:

10 * np.log10(0.5)

# ```python
# -3.010299956639812
# ```

# ## Interferometer Models
#
# TODO make diagram

# ### 2x2 Mach-Zenhder Modulator

from gdsfactory.components import mzi2x2_2x2

mzi2x2_2x2().plot()


# ![mzi2x2_2x2](../_static/img/examples/06a_analytical_mzm_model/mzi2x2_2x2.png)

# The total transfer-matrix model transmission can be computed from multiplying the transfer together for an equivalent field input analysis. Let's consider this in the case of a symmetric 50:50 2x2 coupler matrix and a lossless phase shifter model as above:
#
# \begin{equation}
# [E_O] = [C_{out}] [\phi] [C_{in}] E_{in}
# \end{equation}

# In simplified terms:
#
# \begin{equation}
# \begin{bmatrix}
# 0.707 & 0.707j \\
# 0.707j & 0.707
# \end{bmatrix}
# \begin{bmatrix}
# e^{-j \phi_1} & 0 \\
# 0 & e^{-j \phi_2}
# \end{bmatrix}
# \begin{bmatrix}
# 0.707 & 0.707j \\
# 0.707j & 0.707
# \end{bmatrix}
# \begin{bmatrix}
# E_{o2} \\
# E_{o1}
# \end{bmatrix}
# \end{equation}
#
# \begin{equation}
# \begin{bmatrix}
# 0.707 e^{-j \phi_1} & 0.707j e^{-j \phi_2} \\
# 0.707j e^{-j \phi_1} & 0.707 e^{-j \phi_2}
# \end{bmatrix}
# \begin{bmatrix}
# 0.707 & 0.707j \\
# 0.707j & 0.707
# \end{bmatrix}
# \begin{bmatrix}
# E_{o2} \\
# E_{o1}
# \end{bmatrix}
# \end{equation}
#
# \begin{equation}
# \begin{bmatrix}
# 0.5 e^{-j \phi_1} - 0.5 e^{-j \phi_2} & 0.5j e^{-j \phi_1} + 0.5j e^{-j \phi_2} \\
# 0.5j e^{-j \phi_1} + 0.5j e^{-j \phi_2} & 0.5 e^{-j \phi_1} + 0.5 e^{-j \phi_2}
# \end{bmatrix}
# \begin{bmatrix}
# E_{o2} \\
# E_{o1}
# \end{bmatrix}
# \end{equation}

# #### Cross Transitions
#
# For a $E_{in} =
# \begin{bmatrix}
# 1 \\
# 0
# \end{bmatrix}$:
#
# \begin{equation}
# \begin{bmatrix}
# E_{o3} \\
# E_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# 0.5 e^{-j \phi_1} - 0.5 e^{-j \phi_2} \\
# 0.5j e^{-j \phi_1} + 0.5j e^{-j \phi_2}
# \end{bmatrix}
# \end{equation}
#
# Assuming there is no phase difference between the arms, or $\phi_1$ = $\phi_2$ = $\phi$, then:
#
# \begin{equation}
# \begin{bmatrix}
# E_{o3} \\
# E_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# 0 \\
# j e^{-j \phi}
# \end{bmatrix}
# \end{equation}
#
# Hence, the power (intensity) observed at the output is:
#
# \begin{equation}
# \begin{bmatrix}
# I_{o3} \\
# I_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# 0 \\
# 1
# \end{bmatrix}
# \end{equation}
#
# This is effectively a "cross" transition from inputs to outputs.

# #### Bar Transitions
#
# If we instead assume that there is a $\pi$ phase difference, or $\phi_1 + \phi_2 = \pi = \Delta \phi$, hence $\phi_1 = \pi - \phi_2$ then:
#
#
# Using Euler's formula, $ e^{-j \pi} = -1 $:
# $$
# e^{-j (\pi - \phi_2)} = e^{-j \pi} e^{j \phi_2} = -e^{j \phi_2}
# $$
#
# then:
#
# \begin{equation}
# \begin{bmatrix}
# E_{o3} \\
# E_{o4}
# \end{bmatrix}=
# \begin{bmatrix}
# -0.5 e^{j \phi_2} - 0.5 e^{-j \phi_2} \\
# -0.5j e^{j \phi_2} + 0.5j e^{-j \phi_2}
# \end{bmatrix}=
# \begin{bmatrix}
# -e^{j \phi_2} \\
# 0
# \end{bmatrix}
# \end{equation}
#
# Hence, the power (intensity) observed at the output is:
#
# \begin{equation}
# \begin{bmatrix}
# I_{o3} \\
# I_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# 1 \\
# 0
# \end{bmatrix}
# \end{equation}
#
# This is considered a "bar" transition.

# ## Phase-Shifter Models

# A phase-shifter can be considered as an "active propagation path" which adds or substracts relative phase in reference to another optical path. If we assume we have two waveguides in parallel in an integrated platform, in order to construct the interferometer, we need to consider the addition of phase $\phi$ onto each of these paths. A more complete model considers the loss $\alpha$ ($\frac{N_p}{m}$) per path length $L$. This can be part of a waveguide model:
#
# ### More Ideal Model
#
# \begin{equation}
# \begin{bmatrix}
# E_{o3} \\
# E_{o4}
# \end{bmatrix} =
# \begin{bmatrix}
# e^{-j \phi_1 - \frac{\alpha_1 L_1}{2}} & 0 \\
# 0 & e^{-j \phi_2 - \frac{\alpha_2 L_2}{2}}
# \end{bmatrix}
# \begin{bmatrix}
# E_{o2} \\
# E_{o1}
# \end{bmatrix}
# \end{equation}

# We can assume that the lossless active phase model for a waveguide can be represented by:
# $$
# e^{-j \phi_1}
# $$


def waveguide_active_phase(phase):
    return jnp.e ** (-1j * phase)


# We can assume that there is only one path that adds relative phase onto the interferometer. TODO verify this properly. Let's say that our relative phase is equivalent to the interferometer model derived above:

bar_waveguide_phase = waveguide_active_phase(jnp.pi)
bar_waveguide_phase

# ```python
# (-1-1.2246467991473532e-16j)
# ```

cross_waveguide_phase = waveguide_active_phase(0)
cross_waveguide_phase

# ```python
# (1+0j)
# ```

# We can verify our `sax` measurement in relation to this:

ideal_optical_logic_models = piel.models.frequency.get_default_models(
    type="optical_logic_verification"
)
ideal_optical_logic_models

ideal_optical_logic_models["straight_heater_metal_simple"](active_phase_rad=0)

# ```python
# {('o1', 'o2'): Array(1.+0.j, dtype=complex128, weak_type=True),
#  ('o2', 'o1'): Array(1.+0.j, dtype=complex128, weak_type=True)}
# ```

ideal_optical_logic_models["straight_heater_metal_simple"](active_phase_rad=np.pi)

# ```python
# {('o1', 'o2'): Array(-1.-1.2246468e-16j, dtype=complex128, weak_type=True),
#  ('o2', 'o1'): Array(-1.-1.2246468e-16j, dtype=complex128, weak_type=True)}
# ```

# ###  Model Silicon Perturbation Effects (WIP)

# \begin{equation}
# \phi_1 = \frac{2 \pi}{\lambda_0} [n_{eff,1} L_{nm1} + n_{eff,1}(V) L_{active,1} + n_{eff,1}(T) L_{thermal1}]
# \end{equation}
#
# \begin{equation}
# \phi_2 = \frac{2 \pi}{\lambda_0} [n_{eff,2} L_{nm2} + n_{eff,2}(V) L_{active,2} + n_{eff,2}(T) L_{thermal2}]
# \end{equation}
#
# Note that one assumption is that the lengths are not intertwined or shared between the effects: ie. you don't have a heater on top of an electo-optic modulator for example, and the lengths are not shared.
#
# Hence it can be written that:
#
# \begin{equation}
# n_{eff, i} L_i = n_{eff,i} L_{nm,i} + n_{eff,i}(V) L_{active,i} + n_{eff,i}(T) L_{thermal,i}
# \end{equation}
#
# Hence we know:
# \begin{equation}
# \Delta \phi = \phi_2 - \phi_1
# \end{equation}
#
# Or
# \begin{equation}
# \Delta \phi = \frac{2 \pi (n_{eff, 2}L_2 - n_{eff, 1}L_1)}{\lambda_0}
# \end{equation}
#
# In a balanced MZI, $L_1 = L_2$:
# \begin{equation}
# \Delta \phi = \beta L = \frac{2 \pi \Delta n_{eff} L }{\lambda_0}
# \end{equation}

# For thermal phase shifter purposes:
#
# \begin{equation}
# \frac{\delta \phi}{\delta T} = \frac{2 \pi}{\lambda} \left ( L \frac{dn}{dT} + n \frac{dL}{dT} \right ) = \frac{2 \pi L}{\lambda} \left ( \frac{dn}{dT} (T) + n(T) \alpha (T) \right )
# \end{equation}

# Note that $\frac{2\pi}{\lambda}$ is a standard constant within $\beta$:
#
# Hence
#
# \begin{equation}
# n_{eff,i}(T) L_{thermal,i}(T) =   L \frac{dn}{dT} + n \frac{dL}{dT}  =  \frac{dn}{dT} (T) + n(T) \alpha_T (T)
# \end{equation}

#

# We know FSR:
#
# \begin{equation}
# FSR = \frac{\lambda^2}{n_{og} \Delta L}
# \end{equation}

# > Using the simulated effective index of Fig. 2.3, and Eq. 2.2, the optical group index of the
# channel and rib waveguides were obtained and are plotted in Fig. 2.4. This group index
# will be used as the target for the microwave group velocity for the electrode design.
#
# \begin{equation}
# n_{og} = n_{eff} + \lambda_0 \frac{d n_{eff}}{d \lambda}
# \end{equation}

# \begin{equation}
# E_O = E_{in} cos\left[ \left( \frac{\Delta \beta_2 - \Delta \beta_1}{2} \right) L \right] e^{j \left( \frac{\Delta \beta_2 - \Delta \beta_1}{2} \right)}
# \end{equation}

# \begin{equation}
# T = \frac{1}{2} \left[ 1 = sech(\frac{\Delta \alpha L}{2}) cos \left( \frac{2 \pi}{\lambda_0} (n_{eff1} - n_{eff2} )L \right) \right]
# \end{equation}

L = 1
lambda_0_nm = 1550e-9
delta_alpha_range = np.linspace(0, 5, 250)
delta_neff_range = np.linspace(0, 0.001, 250)
neff_alpha_iterations_transmission_simulations = list()
for delta_alpha_i in delta_alpha_range:
    # List all the corresponding files
    for delta_neff_i in delta_neff_range:
        transmission_i = 1 + np.cos(
            2 * np.pi * delta_neff_i * L / lambda_0_nm
        ) / np.cosh(delta_alpha_i * L / 2)
        iteration_values = {
            "lambda": lambda_0_nm,
            "L": L,
            "delta_alpha": delta_alpha_i,
            "delta_neff": delta_neff_i,
            "transmission": transmission_i,
        }
        neff_alpha_iterations_transmission_simulations.append(iteration_values)
# print(results)

# + active=""
# neff_alpha_iterations_transmission_simulations
# -

neff_alpha_iterations_transmission_dataframe = pd.DataFrame(
    neff_alpha_iterations_transmission_simulations
)
neff_alpha_iterations_transmission_dataframe

# +
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

dataframe_selection = neff_alpha_iterations_transmission_dataframe
# Make files.
X = dataframe_selection.delta_alpha
Y = dataframe_selection.delta_neff  # z axial field component
Z_1 = dataframe_selection.transmission  # X-Component
# Z_2 = dataframe_selection.I_y # Y-Component

# Plot the surface.
color_rcp = "#82fe2b"
color_lcp = "#2b82fe"
# ax.plot_trisurf(X, Y, Z_1, edgecolor='none', label=r'$I_{RCP}$');
# ax.plot_trisurf(X, Y, Z_2, edgecolor='none', label=r'$I_{LCP}$');
ax.plot_trisurf(X, Y, Z_1, cmap=cm.plasma)
# ax.plot_trisurf(X, Y, Z_2, color=color_lcp, alpha=1, edgecolor='none', label=r'$I_{LCP}$');

# ax.view_init(elev=0., azim=-210)
ax.view_init(elev=15.0, azim=30)

ax.set_title(
    r"1.55um MZI Transmission - $\Delta \alpha$ & $\Delta n_{eff}$ Variations",
    fontweight="bold",
    fontsize=16,
    y=0.95,
)
ax.set_xlabel(r"$\Delta \alpha$ (Np/m)", fontsize=14)  # , fontweight="bold")
ax.set_ylabel(
    r" $\Delta n_{eff}$", fontsize=14
)  # , fontweight="bold") # TODO more applicable definition
ax.set_zlabel(r"Transmission (u)", fontsize=14)  # , fontweight="bold")
fig.savefig(
    "../_static/img/examples/06a_analytical_mzm_model/transmission_absorption_1550nm.png"
)
# -

# ![transmission_absorption_1550nm](../_static/img/examples/06a_analytical_mzm_model/transmission_absorption_1550nm.png)

delta_alpha = 0
L = 1e-3
delta_neff_range = np.linspace(0, 0.005, 500)
lambda_range = np.linspace(1500e-9, 1600e-9, 500)
lambda_neff_iterations_transmission_simulations = list()
for delta_neff_i in delta_neff_range:
    # List all the corresponding files
    for lambda_i in lambda_range:
        transmission_i = 1 + np.cos(2 * np.pi * delta_neff_i * L / lambda_i) / np.cosh(
            delta_alpha * L / 2
        )
        iteration_values = {
            "lambda": lambda_i,
            "L": L,
            "delta_alpha": delta_alpha,
            "delta_neff": delta_neff_i,
            "transmission": transmission_i,
        }
        lambda_neff_iterations_transmission_simulations.append(iteration_values)
# print(results)

# + active=""
# lambda_neff_iterations_transmission_simulations
# -

lambda_neff_iterations_transmission_dataframe = pd.DataFrame(
    lambda_neff_iterations_transmission_simulations
)
lambda_neff_iterations_transmission_dataframe

# +
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

dataframe_selection = lambda_neff_iterations_transmission_dataframe
# Make files.
X = dataframe_selection["lambda"]
Y = dataframe_selection.delta_neff
Z_1 = dataframe_selection.transmission  # X-Component
# Z_2 = dataframe_selection.I_y # Y-Component

# Plot the surface.
color_rcp = "#82fe2b"
color_lcp = "#2b82fe"
# ax.plot_trisurf(X, Y, Z_1, edgecolor='none', label=r'$I_{RCP}$');
# ax.plot_trisurf(X, Y, Z_2, edgecolor='none', label=r'$I_{LCP}$');
ax.plot_trisurf(X, Y, Z_1, color=color_lcp)
# ax.plot_trisurf(X, Y, Z_2, color=color_lcp, alpha=1, edgecolor='none', label=r'$I_{LCP}$');

# ax.view_init(elev=0., azim=-210)
ax.view_init(elev=30.0, azim=40)

ax.set_title(
    r"MZI Transmission - $\lambda$ & $\Delta n_{eff}$ Variations",
    fontweight="bold",
    fontsize=16,
)
ax.set_xlabel(r"$\lambda$ Wavelength (m)", fontsize=12)  # , fontweight="bold")
ax.set_ylabel(
    r" $\Delta n_{eff}$ ", fontsize=12
)  # , fontweight="bold") # TODO more applicable definition
ax.set_zlabel(r"Transmission (u)", fontsize=12)  # , fontweight="bold")
fig.savefig(
    "../_static/img/examples/06a_analytical_mzm_model/transmission_lambda_1550nm.png"
)
# -

# ![transmission_lambda_1550nm](../_static/img/examples/06a_analytical_mzm_model/transmission_lambda_1550nm.png)

# ### MZI Transfer Matrix Model
#
# Begin with 3dB beamsplitter modelling
# * $\alpha$ Absorption coefficient
# * $\alpha_1$ Optical propagation loss arm 1
# * $\alpha_2$ Optical propagation loss arm 2
# * $\epsilon_1$ Output power ratio arm 1
# * $\epsilon_2$ Output power ratio arm 2
# * $\epsilon$ Power splitting ratio between the two arms
# * $E_1$ Elecric field phasors of the input
# * $E_{Y,01}$ Output of arm 1 of beamsplitter
# * $E_{Y,02}$ Output of arm 2 of beamsplitter
# * $E_{I_{armX}}$ Input beforethe phase shifter region in arm X
# * $E_{O_{armX}}$ Output after the phase shifter region in arm X
# * $L_{nmX}$ Not modulated lengths in arm X
# * $L_{activeX}$ Electrically modulated lengths of each arm
# * $L_{thermalX}$ Thermally modualted lengths of each arm
# * $L = L_{nmX} + L_{thermalX} + L_{activeX} $ Total effective length of each arm
# * $\Delta N_e$ free electron concentration
# * $\Delta N_h$ hole concentrations
# * $m_{ce}^*$ Effective mass of electrons
# * $m_{ch}^*$ Effective mass of holes
# * $[Y]$ Vector of the Y branches (3dB beamsplitters)
# * $w$ angular frequency in which the refractive index is calculated
# * $w'$ integration variable angular frequency for which teh absorption spectrum files is to be integrated
# * $\mu_e$ electron mobility
# * $\mu_h$ hole mobility

# Propagation in ther ams of the interferometer is modeled by modifying the amplitude and phase of the phasors:
#
# \begin{equation}
# \begin{bmatrix}
# E_{O_{arm1}} \\
# E_{O_{arm2}}
# \end{bmatrix} =
# \begin{bmatrix}
# e^{-j \phi_1 - \frac{\alpha_1 L_1}{2}} & 0 \\
# 0 & e^{-j \phi_2 - \frac{\alpha_2 L_2}{2}}
# \end{bmatrix}
# \begin{bmatrix}
# E_{I_{arm1}}\
# E_{I_{arm2}}
# \end{bmatrix}
# \end{equation}
#

# ## Design Tradeoff
#
# Tradespace between:
# * Optical loss
# * Energy consumpiton
# * Fabrication capabilities
# * Modulation speed
#
#
# Electrode design
# * Impedance matching
# * Microwave velocity to the optical wave matching
# * Microwave propagation loss reduction
#
# OpticalModulator2x2 tests
# * Bit-error-rate measurements under different bias and driving voltages
# *

# DC Kerr Electro-optic effect
#
# * $\beta$ Phase constant
# * $E$ Electric Field Strength
# * $\lambda$ wavelength
# * $\lambda_0$ free-space wavelength
# * $\Delta n_{eff}$ Effective refractive index
# * $K$ Kerr Constant
#
# \begin{equation}
# \Delta n = \lambda K E^2
# \end{equation}

# Following [Patel, 2015] MZI electro-optic modulator equations:
#
# \begin{equation}
# \Delta \phi = \beta L = \frac{2 \pi \Delta n_{eff} L }{\lambda_0}
# \end{equation}
#
# This function assumes an overall $\Delta n$ change for a given L length that applies for balanced MZIs with equal $L$ arm lengths.

# To achieve a $\pi$ phase-shift for 2um using this electro-optic refractive index change equation you get:

lambda_0 = 2.050e-6  # 2.050 um
pi_delta_neff_L = np.pi * lambda_0 / (2 * np.pi)
two_pi_delta_neff_L = 2 * np.pi * lambda_0 / (2 * np.pi)
pi_delta_neff_L

# This is a product of $\Delta n_{eff}$ and $L$. Hence you can write the equation as: $x/L = \Delta n_{eff}$

L = np.linspace(1e-4, 3e-3)
pi_delta_n_eff = pi_delta_neff_L / L
two_pi_delta_n_eff = two_pi_delta_neff_L / L
fig, ax = plt.subplots()
ax.plot(L, pi_delta_n_eff, "b-", label=r"$\pi$")
ax.plot(L, two_pi_delta_n_eff, "g--", label=r"$2\pi$")
ax.legend()
ax.set_xlabel(r"$L$ (mm)", size=14)
ax.set_xticklabels(plt.xticks()[0] * 1e3)
ax.set_ylabel(r"$\Delta n_{eff}$", size=14)
ax.set_title(
    "2um Electro-optic refractive index change per effective modulation length"
)
# fig.savefig("img/refractive_index_change_modulation_length.png")

# +
frey_dn_dT = np.array(
    [
        1e-9,  # TODO Check potentially inconsistent? From Komma
        2e-8,  # TODO CHeck potentially inconsistent? From Komma
        5e-7,  # TODO CHeck potentially inconsistent? From Komma
        5.39e-06,
        1.53e-05,
        2.53e-05,
        3.52e-05,
        4.51e-05,
        5.51e-05,
        6.50e-05,
        7.50e-05,
        1.14e-04,
        1.36e-04,
        1.58e-04,
        1.78e-04,
    ]
)

frey_T_measurements = np.array(
    [
        5,  # TODO Check potentially inconsistent? From Komma
        10,  # TODO Check potentially inconsistent? From Komma
        15,  # TODO Check potentially inconsistent? From Komma
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        150,
        200,
        250,
        295,
    ]
)

frey_n = np.array(
    [
        3.42478,
        3.42478,
        3.42478,
        3.42478,
        3.42488,
        3.42508,
        3.42540,
        3.42582,
        3.42633,
        3.42695,
        3.42765,
        3.43234,
        3.43863,
        3.44609,
        3.45352,
    ]
)

dn_dt_dataframe = pd.DataFrame(
    {"dn_dT": frey_dn_dT, "temperature": frey_T_measurements, "n": frey_n}
)
dn_dt_dataframe.to_csv()

# +
fig, ax1 = plt.subplots(figsize=(6, 6))
ax1.set_xlabel(r"Temperature ($K$)", fontsize=14)
ax1.set_ylabel(r"Silicon Thermo-optic Coefficient $\frac{dn}{dT}$", fontsize=14)
ax1.set_yscale("log")
ax1.plot(
    dn_dt_dataframe["temperature"][3:],
    dn_dt_dataframe.dn_dT[3:],
    "go",
    label=r"$\frac{dn}{dT}$",
)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

# color = 'tab:blue'
ax2.set_ylabel(
    "Silicon Absolute Refractive Index", fontsize=14
)  # we already handled the x-label with ax1
ax2.plot(dn_dt_dataframe["temperature"][3:], dn_dt_dataframe.n[3:], "g--", label=r"$n$")
# ax2.tick_params(axis='y', labelcolor=color)
ax1.legend(loc="upper left", fontsize=14)
ax2.legend(loc="lower right", fontsize=14)

ax1.set_title(r"Cryogenic Thermo-optic Parameters", fontweight="bold", fontsize=16)
fig.tight_layout()  # otherwise the right y-label is slightly clipped
fig.savefig("thermo_optic_temperature_dependence.png")
# -

# We note that the thermo-optic coefficient is variable of temperature


# > Insertion loss in $dB$ of the device is determined by subtracting the maximum of
# the transmission from the input power, in decibels:
#
# \begin{equation}
# IL = P_{in, dBm} - P_{max, dBm}
# \end{equation}
#
# > The extinction ratio is defined as the ratio of the maximum power to the minimum power. It can be calculated for the modulated optical signal and for the optical device. The static or optical ER (ER) is a metric of the passive MZM and can be calculated
#  as:
#
# \begin{equation}
# ER = 10log_{10}(\frac{P_{max}}{P_{min}})
# \end{equation}
#
#

# > The modulated ER (ERmod) is determined from the modulated optical signal. In
# decibels, it is expressed as:
#
# \begin{equation}
# ER_{mod} = 10log_{10}(\frac{P_{H}}{P_{L}})
# \end{equation}
#
# > For on-off keying (OOK) modulation, the modulator is biased at quadrature point, which corresponds to
# the mid-point of the linear transmission curve, or -3 dB of the maximum on the decibel
# transmission curve. At the quadrature point, the modulator is in the most linear regime.
# Incidentally, the largest change in transmission for a change in voltage (dT/dV) also occurs around this point.
# >
# > It should be noted that the modulated ER depends on the swing of the driving voltage and also the modulator biasing point. For instance, in OOK modulation, if the biasing point is moved from the quadrature point to a point corresponding to lower output power, i.e., down the transmission curve, then the zero-level optical power of the output (PL) will also decrease. As the power of the modulated zero-level decreases, the modulated ER will increase.

# ![img](./img/modulator_metrics.png)

# > However, the optical modulation amplitude (OMA), which measures the difference
# between the two optical power levels, i.e., the peak-peak height of the eye, will remain
# almost the same. It will be perturbed by the non-linearity of the transfer curve, but in the linear portion of the curve, OMA would mainly change with the driving voltage.
#
# \begin{equation}
# OMA = P_H - P_L
# \end{equation}
#
# > Changing the bias point for a fixed drive voltage also changes the modulated loss
# (ML) (also referred to as bias loss). Modulated loss is the difference between the input power and the
# power of the highest modulated bit
#
# \begin{equation}
# ML[dB] = P_{in,dBm} - P_{H,dBm}
# \end{equation}
#
# > This leads to the definition of the VπLπ figure-of-merit (FOM), which
# can be used to compare the efficiency of modulators. A low value of this FOM indicates a
# more efficient modulator. In silicon, it is important to note that phase shift is non-linear
# with applied voltage, as will be shown with measurement measurements in Section 5.2.
# Therefore, knowing the $V_{\pi} L_{\pi}$ FOM does not allow the accurate calculation of $V_{\pi}$ for a
# given modulator length or the calculation of Lπ for a given voltage
#
# > Theoretical optical extinction ratio can be found by taking the ratio of the transmission
# (Eq. 2.14) at constructive interference and at destructive interference
#
# \begin{equation}
# ER_{theory} = \frac{1 + sech(\frac{\Delta \alpha L}{2})}{1 - sech(\frac{\Delta \alpha L}{2})}
# \end{equation}

# Complex refractive index $\bar{n}$ where $n$ is the real part and $k$ is the extinction coefficient.
#
# \begin{equation}
# \bar{n} = n + jk
# \end{equation}
#
# \begin{equation}
# \alpha = \frac{4 \pi k}{\lambda_0}
# \end{equation}
#
# \begin{equation}
# \Delta n (w) = \frac{c_0}{\pi} PV \int_0^{\infty} \frac{\Delta \alpha(w')}{w^{'2} - w^2} dw'
# \end{equation}
#
# Note that singularity at $w' = w$, and Cauchy principle value denoted by $PV$ must be taken. Absorption spectrum is integrated over entire frequency range such that singulariteis are avoided.
#
# Change of absorption spectrium $\Delta \alpha (w')$ from an applied external electric field can be written as:
#
# \begin{equation}
# \Delta \alpha (w', E) = \alpha(w', E) - \alpha (w', 0)
# \end{equation}
#
# In teh case of change in absorption due to change in carrier concentration $\Delta N$:
#
# \begin{equation}
# \Delta \alpha(w', \Delta N) = \alpha (w', \Delta N) - \alpha (w', 0)
# \end{equation}

# Perturbations in complex refractive index $\bar{n}$ inducted by teh application of electric field (electro-optic effects) or modualting the free carrier concentration.
#
# Several electro-optic effects:
# * Pockels (refractive index change directly proportional to applied electric field only present in non-centrosymmetric crystals, unstrained silicon is centro-symmetric so does not have Pockel's unless deliberately strained)
# * Kerr
# * Franz-Keldysh (electro-absorption)
#
#

# From Soref and Bennet, 1987:
#
# > In silicon, the strongest refractive index change comes from the plasma dispersion effect,
# in which light is scattered by mobile carriers. The presence of free carriers results in shifts
# in the absorption spectrum towards the short and long wavelengths, as well as free carrier
# absorption (FCA). The change in FCA for a change in carrier concentration of holes ∆Nh
# and electrons ∆Ne relative to the intrinsic concentration in a material is predicted by the
# Drude-Lorenz equation
#
# \begin{equation}
# \Delta \alpha = \frac{e^3 \lambda_0^2}{4 \pi^2 c_0^3 \epsilon_0 n} \left ( \frac{\Delta N_e}{\mu_e (m_{ce}^*)^2} + \frac{\Delta N_h}{\mu_h (m_{ch}^*)^2} \right )
# \end{equation}
#
# \begin{equation}
# \Delta n = \frac{-e^2 \lambda_0^2}{8 \pi^2 c_0^2 \epsilon_0 n} \left ( \frac{\Delta N_e}{m_{ce}^*} + \frac{\Delta N_h}{m_{ch}^*} \right )
# \end{equation}

# +
delta_N_e_variations = np.linspace(1e17, 1e20)
delta_N_h_variations = np.linspace(1e17, 1e20)

e_c = 1.602176634e-19  # electronic charge in Coulombs
epsilon_0 = 8.8541878128e-12  # Farads per meter
c_0 = 299792458  # meters per second
n = frey_n[-1]  # At room temperature 2um
m_c_0 = 1
m_c_e = 0.26 * m_c_0
m_c_h = 0.39 * m_c_0
# -

# From Nedeljkovic, "Free-Carrier Electrorefraction and Electroabsorption Modulation Predictionsfor Silicon Over the 1–14-m Infrared Wavelength Range" based on Soref and Bennet:
#
# Assumptions of Soref and Bennet's measurement:
# * > It is well known that n and k are related by the Kramers-Kronig dispersion relations. The same relations hold for An and Ak as discussed below. It has been known for many years that the optical absorption spectrum of silicon is modified by external electric fields (the Franz-Keldysh effect) or by changes in the material’s charge-carrier density. If we start with an measurement knowledge of the modified spectrum Aa(w, E) or Aa(w, AN), then we can compute the change in the index An.
# * > The optical properties of silicon are strongly affected by injection of charge carriers into an undoped sample (AN) or by the removal of free carriers from a doped sample (-AN). However, we are not aware of any measurement results in the Si literature on spectral changes via injection/depletion. There are, on the other hand, numerous literature references to the effects of impurity doping on Si optical properties. Optically, it does not make much difference whether carriers come from impurity ionization or from injection. Thus, an equivalence is assumed here. We draw upon measurement results that show how the a spectrum is changed by a density Ni of impurity atoms in the crystal. The An calculated from that spectrum is assumed to be the An that arises from AN Three carrier effects are important: 1) traditional freecarrier absorption, 2) Burstein-Moss bandfilling that shifts the a spectrum to shorter wavelengths, and 3) Coulombic interaction of carriers with impurities, an effect that shifts the spectrum to longer wavelengths. These act simultaneously. What is actually observed is an a redshift; thus, Coulombic effects are stronger than bandfilling in c-Si (see [ll] and [12]).
# * > We shall consider first the added loss introduced by free electrons or free holes. Theoretical curves from (5) are
# plotted together with the measurement absorption values taken from Schmid [ 1 11 and from Spitzer and Fan [ 131.
# Curves for electrons and holes at the 1.3 and 1.55 pm wavelengths are given as a function of “injected” carrier concentration in Figs. 12-15] Good matching.
# * > The theoretical curves in Figs. 12-15 were obtained by substituting the values m% = 0.26 mo and m:h = 0.39 mo into (5). The mobility values used in (5) were taken from Fig. 2.3.1 of Wolf [21].
# * > With the aid of x-y lines drawn on Figs. 5 and 7, the (a, w) files were digitized and entered into the computer, and the absorption spectrum of pure material was subtracted point by point from each of the quantized a(AN) curves to give a set of Aa values that were inserted into the numerator of (2). With our trapezoid-rule program, we calculated the integral (2) over the range I/ = 0.001- 2.8 V, and we took Ni = AN. This produced the result shown in Fig. 8 for free electrons and the result of Fig. 9 for free holes. Figs. 8 and 9 are plots of An as a function of wavelength from 1 .O to 2.0 pm with AN as a parameter. The increase of An with X is approximately quadratic. Next, we used the results of Figs. 8 and 9 to determine the carrier-concentration dependence of An at the fiberoptic wavelengths: X = 1.3 or 1.55 pm. Those results are shown in Figs. 10 and 11. The curves presented in Figs. 10 and 11 are least squares fit to the files points obtained from Figs. 8 and 9. In Fig. 10 (X = 1.3 pm), the freehole files are fitted with a line of slope +0.805, while the free-electron files are fitted with a + 1.05 slope line. In Fig. 14 (X = 1.55 pm), the fitted slopes are +0.818(holes) and +l.O4(electrons). It is interesting to compare the predictions of a simple free-carrier or Dmde model of c-Si to our An results and to measurement Aa files. The well-known formulas for refraction and absorption due to free electrons and free holes are as follows:
# * Does not account for temperature dependence
#
# From
# \begin{equation}
# \Delta \alpha (\lambda) = \Delta \alpha_e (\lambda) + \Delta \alpha_h (\lambda) = a (\lambda) \Delta N_e ^{b (\lambda)} + c(\lambda) \Delta N_h ^{d (\lambda)}
# \end{equation}
#
# \begin{equation}
# - \Delta n (\lambda) = \Delta n_e (\lambda) + \Delta n_h (\lambda) = p (\lambda) \Delta N_e ^{q (\lambda)} + r(\lambda) \Delta N_h ^{s (\lambda)}
# \end{equation}

# Least-squares matching coefficients from  Nedeljkovic, "Free-Carrier Electrorefraction and Electroabsorption Modulation Predictionsfor Silicon Over the 1–14-m Infrared Wavelength Range"

#
#

a_2um = 3.22e-20
b_2um = 1.149
c_2um = 6.21e-20
d_2um = 1.119
p_2um = 1.91e-21
q_2um = 0.992
r_2um = 2.28e-18
s_2um = 0.841

delta_hole_electron_concentration_iterations_index_absorption_simulations = list()
for delta_N_e_i in delta_N_e_variations:
    # List all the corresponding files
    for delta_N_h_i in delta_N_h_variations:
        delta_alpha_i = a_2um * (delta_N_e_i) ** b_2um + c_2um * (delta_N_h_i) ** d_2um
        delta_n_i = -(p_2um * (delta_N_e_i) ** q_2um + r_2um * (delta_N_h_i) ** s_2um)
        iteration_values = {
            "delta_alpha": delta_alpha_i,
            "delta_n": delta_n_i,
            "delta_N_h": delta_N_h_i,
            "delta_N_e": delta_N_e_i,
        }
        delta_hole_electron_concentration_iterations_index_absorption_simulations.append(
            iteration_values
        )
# print(results)

delta_hole_electron_concentration_iterations_index_absorption_dataframe = pd.DataFrame(
    delta_hole_electron_concentration_iterations_index_absorption_simulations
)
delta_hole_electron_concentration_iterations_index_absorption_dataframe

# +
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

dataframe_selection = (
    delta_hole_electron_concentration_iterations_index_absorption_dataframe
)
# Make files.
X = dataframe_selection.delta_N_h
Y = dataframe_selection.delta_N_e
Z_1 = dataframe_selection.delta_alpha  # X-Component
# Z_2 = dataframe_selection.I_y # Y-Component

# Plot the surface.
# color_rcp = "#82fe2b"
# color_lcp = "#2b82fe"
# ax.plot_trisurf(X, Y, Z_1, edgecolor='none', label=r'$I_{RCP}$');
# ax.plot_trisurf(X, Y, Z_2, edgecolor='none', label=r'$I_{LCP}$');
ax.plot_trisurf(
    X, Y, Z_1, cmap=cm.coolwarm
)  # color=color_rcp, alpha=1, edgecolor='none', label=r'$I_{RCP}$');
# ax.plot_trisurf(X, Y, Z_2, color=color_lcp, alpha=1, edgecolor='none', label=r'$I_{LCP}$');

# ax.view_init(elev=0., azim=-210)
ax.view_init(elev=5.0, azim=-60)
"""

ax.set_xlabel(r'Change in Hole Concentration $\Delta N_h$', fontsize =12)#, fontweight="bold")
ax.set_ylabel(r'Change in Electron Concentration $\Delta N_e$', fontsize =12)#, fontweight="bold") # TODO more applicable definition
ax.set_zlabel(r'Change in Attenuation $\Delta \alpha$', fontsize =12)#, fontweight="bold")
"""
ax.set_title(
    r"Attenuation change $\Delta \alpha$ as a variation of carrier concentrations",
    fontweight="bold",
    fontsize=16,
)
ax.set_xlabel(r"$\Delta N_h$", fontsize=14)
ax.set_ylabel(r"$\Delta N_e$", fontsize=14)
ax.set_zlabel(r"$\Delta \alpha$", fontsize=14)

# -

delta_N_h_standalone_variation_Ne_1e17_dataframe = dataframe_selection[
    dataframe_selection.delta_N_e == 1.000000e17
]
delta_N_e_standalone_variation_Nh_1e17_dataframe = dataframe_selection[
    dataframe_selection.delta_N_h == 1.000000e17
]
plt.plot(
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_N_h,
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_alpha,
    label=r"$\Delta N_h$ (Nedeljkovic)",
)
plt.plot(
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_N_e,
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_alpha,
    label=r"$\Delta N_e$ (Nedeljkovic)",
)
plt.legend()
plt.ylabel(r"$\Delta \alpha$", fontsize=12)
plt.xlabel(r"Carrier Concentration Change $\Delta N$ [$cm^{-3}$]", fontsize=12)
plt.title(
    r"Standalone Dopant Concentration Changes Variations (Constant 1e17) Effects - Attenuation $\Delta \alpha$"
)
plt.xscale("log")

# +
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

dataframe_selection = (
    delta_hole_electron_concentration_iterations_index_absorption_dataframe
)
# Make files.
X = dataframe_selection.delta_N_h
Y = dataframe_selection.delta_N_e
Z_1 = dataframe_selection.delta_n  # X-Component
# Z_2 = dataframe_selection.I_y # Y-Component

# Plot the surface.
color_rcp = "#82fe2b"
color_lcp = "#2b82fe"
# ax.plot_trisurf(X, Y, Z_1, edgecolor='none', label=r'$I_{RCP}$');
# ax.plot_trisurf(X, Y, Z_2, edgecolor='none', label=r'$I_{LCP}$');
ax.plot_trisurf(X, Y, Z_1, cmap=cm.coolwarm)
# ax.plot_trisurf(X, Y, Z_2, color=color_lcp, alpha=1, edgecolor='none', label=r'$I_{LCP}$');

# ax.view_init(elev=0., azim=-210)
ax.view_init(elev=15.0, azim=-30)

"""
ax.set_title(r'Absolute refractive index changes  $\Delta n$ as a variation of carrier concentration', fontweight="bold", fontsize=16)
ax.set_xlabel(r'Change in Hole Concentration $\Delta N_h$')# , fontsize =10, labelpad=10)#, fontweight="bold")
ax.set_ylabel(r'Change in Electron Concentration $\Delta N_e$')# , fontsize =10, labelpad=10)#, fontweight="bold") # TODO more applicable definition
ax.set_zlabel(r'Change in Refractive Index $\Delta n$')# , fontsize =10, labelpad=10)#, fontweight="bold")
"""

ax.set_title(
    r"Absolute refractive index changes  $\Delta n$ as a variation of carrier concentration",
    fontweight="bold",
    fontsize=16,
)
ax.set_xlabel(r"$\Delta N_h$", fontsize=14)
ax.set_ylabel(r"$\Delta N_e$", fontsize=14)
ax.set_zlabel(r"$\Delta n$", fontsize=14)

# -

plt.plot(
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_N_h,
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_n,
    label=r"$\Delta N_h$ (Nedeljkovic)",
)
plt.plot(
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_N_e,
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_n,
    label=r"$\Delta N_e$ (Nedeljkovic)",
)
plt.legend()
plt.ylabel(r"$\Delta n$", fontsize=12)
plt.xlabel(r"Carrier Concentration Change $\Delta N$ [$cm^{-3}$]", fontsize=12)
plt.title(
    r"Standalone Dopant Concentration Changes Variations Effects (Constant 1e17) - Refractive Index $\Delta n$"
)
plt.xscale("log")

# +
# dn_dt_dataframe = pd.DataFrame({"dn_dT": frey_dn_dT, "temperature": frey_T_measurements, "n": frey_n })


fig, ax1 = plt.subplots(figsize=(8, 4))
# ax1.set_xlabel(r"Carrier Concentration Change $\Delta N$ [$cm^{-3}$]", fontsize=12)
ax1.set_ylabel(r"Absorption Coefficient $\Delta \alpha$ $[cm^{-1}]$", fontsize=12)
# ax1.set_yscale("log")
# ax1.plot(dn_dt_dataframe["temperature"][3:], dn_dt_dataframe.dn_dT[3:], "go", label=r"$\frac{dn}{dT}$")


delta_N_h_standalone_variation_Ne_1e17_dataframe = dataframe_selection[
    dataframe_selection.delta_N_e == 1.000000e17
]
delta_N_e_standalone_variation_Nh_1e17_dataframe = dataframe_selection[
    dataframe_selection.delta_N_h == 1.000000e17
]

ax1.set_yscale("log")
ax1.plot(
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_N_h,
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_alpha,
    "b-",
    label=r"$\Delta \alpha(\Delta N_h$)",
)
ax1.plot(
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_N_e,
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_alpha,
    "m-.",
    label=r"$\Delta \alpha(\Delta N_e$)",
)
ax1.legend(loc="upper left", fontsize=14)
ax1.set_xscale("log")


ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel(r"$\Delta n$", fontsize=14)
ax2.plot(
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_N_h,
    delta_N_h_standalone_variation_Ne_1e17_dataframe.delta_n,
    "b--",
    label=r"$\Delta n(\Delta N_h$)",
)
ax2.plot(
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_N_e,
    delta_N_e_standalone_variation_Nh_1e17_dataframe.delta_n,
    "m:",
    label=r"$\Delta n(\Delta N_e$)",
)
ax2.set_ylabel(r"Refractive Index $\Delta n$", fontsize=14)
ax2.legend(loc="lower right", fontsize=14)

ax1.set_xlabel(r"Carrier Concentration Change $\Delta N$ [$cm^{-3}$]", fontsize=14)
# plt.title(r"Standalone Dopant Concentration Changes Variations Effects (Constant 1e17) - Refractive Index $\Delta n$")


ax1.set_title(
    r"Nedeljkovic Dopant Concentration Variations (1e17)",
    fontweight="bold",
    fontsize=16,
)
fig.tight_layout()  # otherwise the right y-label is slightly clipped
fig.savefig("nedeljkovic_dopant_concentration_variations.png")
# -
