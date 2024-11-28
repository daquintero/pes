"""
TODO implement this function.
In this function we implement different methods of mapping electronic signals to phase.

One particular implementation of phase mapping would be:

.. list-table:: Example Basic Phase Mapping
   :header-rows: 1

   * - Bit
     - Phase
   * - b0
     - :math:`\\phi_0 \\to 0`
   * - b1
     - :math:`\\phi_1 \\to \\pi`

We can define the two corresponding angles that this would be.

A more complex implementation of phase mapping can be similar to a DAC mapping: a bitstring within a converter
bit-size can map directly to a particular phase space within a particular mapping."""

import numpy as np
from ..electronic.digital import bits_array_from_bits_amount
from ....types.digital_electro_optic import BitPhaseMap


def linear_bit_phase_map(
    bits_amount: int,
    final_phase_rad: float,
    initial_phase_rad: float = 0,
    quantization_error: float = 0.000001,
    **kwargs,
) -> BitPhaseMap:
    """
    Returns a linear direct mapping of bits to phase.

    Args:
        bits_amount(int): Amount of bits to generate.
        final_phase_rad(float): Final phase to map to.
        initial_phase_rad(float): Initial phase to map to.
        quantization_error(float): Error in the phase mapping.

    Returns:
        BitPhaseMap: Mapping of bits to phase.
    """
    # Generate the binary combinations for the specified bit amount
    bits_array = bits_array_from_bits_amount(bits_amount)

    # Calculate the number of divisions in the phase space
    phase_division_amount = len(bits_array) - 1

    # Calculate the step size for each phase division, adjusting for quantization error
    phase_division_step = (
        final_phase_rad - initial_phase_rad
    ) / phase_division_amount - quantization_error

    # Generate the phase array using numpy's arange
    linear_phase_array = np.arange(
        initial_phase_rad, final_phase_rad, phase_division_step
    )

    # Ensure that we have enough phases for all bits; handle edge cases where rounding might cause fewer steps
    if len(linear_phase_array) < len(bits_array):
        linear_phase_array = np.append(linear_phase_array, final_phase_rad)

    # Create the BitPhaseMap object
    bit_phase_mapping = BitPhaseMap(bits=bits_array, phase=linear_phase_array)

    return bit_phase_mapping
