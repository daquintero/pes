import numpy as np
from piel.types import TimeSignalData, Unit
import logging

logger = logging.getLogger(__name__)


def resize_data_time_signal_units(
    waveform: TimeSignalData,
    time_unit: Unit,
    data_unit: Unit,
    corrected_name_suffix: str = "_corrected",
) -> TimeSignalData:
    """
    Applies unit corrections to the time and data arrays of a TimeSignalData object.

    Parameters:
    - waveform: The original waveform data.
    - time_unit: The unit to apply to the time axis.
    - data_unit: The unit to apply to the data.
    - corrected_name_suffix: Suffix to append to the data name after correction.

    Returns:
    - A new TimeSignalData object with corrected time and data.
    """
    # Convert time and data to NumPy arrays for efficient computation
    time_array = np.array(waveform.time_s, dtype=float)
    data_array = np.array(waveform.data, dtype=float)

    # Apply time correction if time_unit is a Unit instance
    if isinstance(time_unit, Unit):
        if time_unit.base != 1:
            logger.debug(
                f"Data correction of 1/{time_unit.base} from unit definition '{time_unit}' will be applied on the time axis."
            )
            corrected_time = time_array / time_unit.base
        else:
            corrected_time = time_array
    else:
        # If time_unit is not a Unit instance, assume no correction
        corrected_time = time_array

    # Apply data correction if data_unit is a Unit instance
    if isinstance(data_unit, Unit):
        if data_unit.base != 1:
            logger.debug(
                f"Data correction of 1/{data_unit.base} from unit definition '{data_unit}' will be applied on the data."
            )
            corrected_data = data_array / data_unit.base
        else:
            corrected_data = data_array
    else:
        # If data_unit is not a Unit instance, assume no correction
        corrected_data = data_array

    # Append the suffix to the data name
    corrected_data_name = f"{waveform.data_name}{corrected_name_suffix}"

    # Create and return the corrected waveform
    return TimeSignalData(
        time_s=corrected_time.tolist(),  # Convert back to list if necessary
        data=corrected_data.tolist(),
        data_name=corrected_data_name,
    )
