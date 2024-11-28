from typing import Literal

from piel.types.core import NumericalTypes
from piel.types.symbolic import SymbolicValue
from piel.base.units import (
    unit_radd,
    unit_add,
    unit_mul,
    unit_rmul,
    unit_truediv,
    unit_rtruediv,
)

BaseSIUnitNameList = Literal[
    "meter",
    "second",
    "mole",
    "ampere",
    "volt",
    "kelvin",
    "candela",
    "watt",
    "dBm",
    "Hertz",
    "Decibel",
    "meter_squared",
]


class Unit(SymbolicValue):
    datum: BaseSIUnitNameList | str
    base: NumericalTypes = 1
    """In the format 1eN"""

    __mul__ = unit_mul
    __rmul__ = unit_rmul
    __add__ = unit_add
    __radd__ = unit_radd
    __truediv__ = unit_truediv
    __rtruediv__ = unit_rtruediv


A = Unit(name="ampere", datum="ampere", base=1, label=r"Current $A$", shorthand="A")
dB = Unit(name="decibel", datum="dB", base=1, label=r"Magnitude $dB$", shorthand="dB")
dBm = Unit(
    name="decibel_milliwatt", datum="dBm", base=1, label=r"Power $dBm$", shorthand="dBm"
)
degree = Unit(name="degree", datum="1", base=1, label=r"Degree", shorthand="degree")
GHz = Unit(
    name="gigahertz", datum="hertz", base=1e9, label=r"Frequency $GHz$", shorthand="GHz"
)
Hz = Unit(name="hertz", datum="hertz", base=1, label=r"Frequency $Hz$", shorthand="Hz")
H = Unit(name="Henry", datum="henry", base=1, label=r"Henry $H$", shorthand="H")
nm = Unit(
    name="nanometer", datum="meter", base=1e-9, label=r"Length $nm$", shorthand="nm"
)
ns = Unit(
    name="nanosecond", datum="second", base=1e-9, label=r"Time $ns$", shorthand="ns"
)
m = Unit(name="meter", datum="meter", base=1, label=r"Length $m$", shorthand="m")
MHz = Unit(
    name="megahertz", datum="hertz", base=1e6, label=r"Frequency $MHz$", shorthand="MHz"
)
mm2 = Unit(
    name="millimeter_squared",
    datum="meter_squared",
    base=1e-6,
    label=r"Area $mm^2$",
    shorthand="mm2",
)
mW = Unit(name="miliwatt", datum="watt", base=1e-3, label=r"Power $mW$", shorthand="mW")
ohm = Unit(
    name="ohm",
    datum="resistance",
    base=1,
    label=r"Resistance $\Omega$",
    shorthand=r"ohm",
)
ps = Unit(
    name="picosecond", datum="second", base=1e-12, label=r"Time $ps$", shorthand="ps"
)
ratio = Unit(name="ratio", datum="1", base=1, label=r"Ratio $u$", shorthand="ratio")
s = Unit(name="second", datum="second", base=1, label=r"Time $s$", shorthand="s")
us = Unit(
    name="microsecond", datum="second", base=1e-6, label=r"Time $\mu s$", shorthand="us"
)
W = Unit(name="watt", datum="watt", base=1, label=r"Power $W$", shorthand="W")
V = Unit(name="Volt", datum="voltage", base=1, label=r"Voltage $V$", shorthand="V")

# TODO implement operational units
