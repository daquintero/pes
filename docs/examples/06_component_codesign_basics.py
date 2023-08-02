# # Component Codesign Basics

# When we have photonic components driven by electronic devices, there is a scope that we might want to optimise certain devices to be faster, smaller, or less power-consumptive. It can be complicated to do this just analytically, so we would like to have the capability of integrating our design software for each of our devices with our simulation software of our electronics. There might be multiple  software tools to design different devices, and the benefit of integrating these tools via open-source is that co-design becomes much more feasible and meaningful.
#
# In this example, we will continue exploring the co-design of a thermo-optic phase shifter in continuation of all the previous examples. However, this time, we will perform some optimisation in its design parameters and related. We will use the `femwell` package that is part of the `GDSFactory` suite.
#
# ## Start from Femwell `TiN TOPS heater` example
#
# We will begin by extracting the electrical parameters of the basic `TiN TOPS heater` example provided in [`femwell`](https://helgegehring.github.io/femwell/photonics/examples/metal_heater_phase_shifter.html). We will create a function where we change the width of the heater, and we explore the change in resistance, but also in thermo-optic phase modulation efficiency.
