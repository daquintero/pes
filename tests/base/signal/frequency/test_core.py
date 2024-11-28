from piel.types import Phasor, Hz, degree, V
from piel.base.signal.frequency.core import (
    offset_phasor_magnitude,
)  # Replace 'your_module' with the actual module name


def test_offset_with_int_magnitude():
    phasor = Phasor(
        magnitude=10,
        phase=30,
        frequency=60,
        frequency_unit=Hz,
        phase_unit=degree,
        magnitude_unit=V,
    )
    offset = 5
    new_phasor = offset_phasor_magnitude(phasor, offset)

    assert new_phasor.magnitude == 15, "Magnitude should be incremented by offset"
    assert new_phasor.phase == phasor.phase, "Phase should remain unchanged"
    assert new_phasor.frequency == phasor.frequency, "Frequency should remain unchanged"
    assert (
        new_phasor.frequency_unit == phasor.frequency_unit
    ), "Frequency unit should remain unchanged"
    assert (
        new_phasor.phase_unit == phasor.phase_unit
    ), "Phase unit should remain unchanged"
    assert (
        new_phasor.magnitude_unit == phasor.magnitude_unit
    ), "Magnitude unit should remain unchanged"
