import numpy as np
from piel.types.units import m, s, H
from piel.types.quantity import Quantity


c = Quantity(name="speed_of_light", value=299792458, unit=m / s)
mu_0 = Quantity(name="permeability_free_space", value=(4 * np.pi * 1e-7), unit=H / m)
