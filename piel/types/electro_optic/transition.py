"""
This module defines the OpticalStateTransitionCollection class and related measurement for managing phase transitions in electro-optic measurement.
It also provides a typed dictionary for Fock state phase transitions and includes necessary imports and type aliases.
"""

import pandas as pd
from pydantic import ConfigDict
from typing import Literal, Optional
from typing_extensions import TypedDict
from piel.types.core import ArrayTypes, PielBaseModel, TupleNumericalType, TupleIntType

# Type alias for phase maps, which can be either a tuple of floats or a tuple of integers.
PhaseMapType = TupleNumericalType
"""
PhaseMapType: Alias for phase map measurement.
    Can be one of:
    - TupleFloatType: A tuple of float values.
    - TupleIntType: A tuple of integer values.
"""


class FockStatePhaseTransition(TypedDict):
    """
    A typed dictionary representing a phase transition for Fock states in an electro-optic model.

    Attributes:
        phase (PhaseMapType): The phase mapping for the transition.
        input_fock_state (TupleIntType): The input Fock state as a tuple of integers.
        output_fock_state (TupleIntType): The output Fock state as a tuple of integers.
        target_mode_output (Optional[bool | int]): Indicates whether the target mode is output (1 or True) or not (0 or False).
    """

    phase: PhaseMapType
    input_fock_state: TupleIntType
    output_fock_state: TupleIntType
    target_mode_output: Optional[bool | int] | None


# Literal type representing possible phase transition measurement in an optical model.
PhaseTransitionTypes = Literal["cross", "bar"]
"""
PhaseTransitionTypes: A literal type for phase transition measurement.
    Can be one of:
    - "cross": Refers to a cross-type phase transition.
    - "bar": Refers to a bar-type phase transition.
"""

OpticalTransmission = FockStatePhaseTransition


class OpticalStateTransitionCollection(PielBaseModel):
    """
    A model representing transitions between optical states, specifically for Fock states in an electro-optic system.

    Attributes:
        mode_amount (int): The number of modes in the system.
        target_mode_index (int): The index of the target mode in the system.
        transmission_data (list[FockStatePhaseTransition]): A list of Fock state phase transition mappings.

    Properties:
        transition_dataframe (pd.DataFrame): A DataFrame representation of the transmission files.
        target_output_dataframe (pd.DataFrame): A DataFrame filtered to include only the transitions where target_mode_output is 1.
    """

    # List of keys to ignore
    _ignore_keys: list[str] = ["unitary", "raw_output"]
    model_config = ConfigDict(extra="allow")

    mode_amount: int | None = None
    """
    mode_amount (int):
        The number of modes in the system.
    """

    target_mode_index: int | None = None
    """
    target_mode_index (int):
        The index of the target mode in the system.
    """

    transmission_data: list[OpticalTransmission]
    """
    transmission_data (list[FockStatePhaseTransition]):
        A list of dictionaries representing the phase transitions for Fock states.
    """

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Returns a full pandas DataFrame representation of the transmission files.

        Returns:
            pd.DataFrame: A DataFrame containing the transmission files for the optical states.
        """
        return pd.DataFrame(self.transmission_data)

    @property
    def keys_list(self) -> list[str]:
        """
        Returns a list of keys from the first entry in the transmission files, excluding specified keys.

        Returns:
            List[str]: A list of keys from the first transmission files entry, excluding the keys specified in `_ignore_keys`.

        Notes:
            The keys specified in `_ignore_keys` will be excluded from the list of connection.
        """
        if not self.transmission_data:
            return []

        # Get keys from the first entry in the transmission files and exclude specified keys
        return [
            key
            for key in self.transmission_data[0].keys()
            if key not in self._ignore_keys
        ]

    @property
    def transition_dataframe(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame representation of the transmission files, excluding specific keys.

        Returns:
            pd.DataFrame: A DataFrame containing the transmission files for the optical states, with specified keys excluded.

        Notes:
            The keys 'unitary' and 'raw_output' will be excluded from the transmission files.
        """

        # Filter out the specified keys from each dictionary in the list
        filtered_data = [
            {k: v for k, v in entry.items() if k not in self._ignore_keys}
            for entry in self.transmission_data
        ]

        # Create a DataFrame from the filtered files
        return pd.DataFrame(filtered_data)

    @property
    def target_output_dataframe(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame filtered to include only the transitions where target_mode_output is 1.

        Returns:
            pd.DataFrame: A DataFrame containing only the transitions where the target mode is an output.
        """
        # TODO: add verification eventually
        return self.transition_dataframe[
            self.transition_dataframe["target_mode_output"] == 1
        ]


SwitchFunctionParameter = dict
SParameterCollection = dict[int, ArrayTypes]
