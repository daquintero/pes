def offset_phasor_magnitude(phasor, offset: float):
    from piel.types import Phasor

    assert isinstance(phasor, Phasor)
    # TODO: Else convert to Phasor if PhasorType

    """Return a new Phasor with its magnitude offset by the given value."""
    # Determine the new magnitude with the offset
    if isinstance(phasor.magnitude, (int, float)):
        new_magnitude = phasor.magnitude + offset
    elif isinstance(phasor.magnitude, list):
        new_magnitude = [m + offset for m in phasor.magnitude]
    else:
        raise TypeError("Unsupported type for magnitude in Phasor")

    # Create a new Phasor with the updated magnitude and other unchanged properties
    new_phasor = Phasor(
        magnitude=new_magnitude,
        phase=phasor.phase,
        frequency=phasor.frequency,
        frequency_unit=phasor.frequency_unit,
        phase_unit=phasor.phase_unit,
        magnitude_unit=phasor.magnitude_unit,
    )

    return new_phasor
