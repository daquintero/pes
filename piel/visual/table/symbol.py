from typing import Union
import logging

logger = logging.getLogger(__name__)


def convert_to_pi_fraction(
    value: Union[float, int, str], max_denominator: int = 100
) -> str:
    """
    Converts a number to the closest fraction of π in LaTeX format if possible.

    Args:
        value (Union[float, int, str]): The input number or string representing a number.
        max_denominator (int): The maximum denominator for the fraction (default is 100).

    Returns:
        str: A LaTeX string representation of the number as a fraction of π if possible.

    Examples:
        >>> closest_pi_fraction(3.14159)
        '\\pi'

        >>> closest_pi_fraction(1.0472)
        '\\frac{\\pi}{3}'

        >>> closest_pi_fraction(0.523599)
        '\\frac{\\pi}{6}'

        >>> closest_pi_fraction(1)
        '1'
    """
    from sympy import pi, nsimplify, latex

    try:
        # Convert to float if input is a string
        if isinstance(value, str):
            value = float(value)

        # Find the ratio of the value to π and simplify it
        multiple_of_pi = value / pi.evalf()
        rational_approx = nsimplify(
            multiple_of_pi,
            rational=True,
            tolerance=1e-10,
        )

        logger.debug(rational_approx)

        # If the approximation is zero, return '0'
        if rational_approx == 0:
            return "0"
        elif rational_approx == 1:
            return "\\pi"
        elif rational_approx == -1:
            return "-\\pi"
        elif rational_approx.q == 1:
            # If it simplifies to an integer multiple of π
            return f"{rational_approx.p}\\pi"
        else:
            # Fractional multiple of π
            return f"\\frac{{{rational_approx.p}\\pi}}{{{rational_approx.q}}}"
    except Exception:
        # Fallback to returning the number in LaTeX format if it cannot be simplified with π
        return latex(value)


def convert_tuple_to_pi_fractions(
    values: tuple[Union[int, float, str], ...],
) -> tuple[str, ...]:
    """
    Converts each element in a tuple of numbers to a fraction of π in LaTeX format if possible.

    Args:
        values (Tuple[Union[int, float, str], ...]): A tuple of numbers or strings representing numbers.

    Returns:
        Tuple[str, ...]: A tuple of LaTeX string representations for each number as a fraction of π if possible.

    Examples:
        >>> convert_tuple_to_pi_fractions((3.14159, 1.5708, 1))
        ('\\pi', '\\frac{\\pi}{2}', '1')

        >>> convert_tuple_to_pi_fractions((0.785398, 0.523599, 0))
        ('\\frac{\\pi}{4}', '\\frac{\\pi}{6}', '0')
    """
    phase_tuple = tuple(convert_to_pi_fraction(value) for value in values)
    separator = ","
    out = "[" + separator.join(phase_tuple) + "]"
    return out
