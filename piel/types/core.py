import jax.numpy as jnp
import numpy as np
import os
import pathlib
import pydantic
import types
from typing import Literal

# Type aliases for various path and array measurement used throughout the module.
PathTypes = str | pathlib.Path | os.PathLike | types.ModuleType
ArrayTypes = np.ndarray | jnp.ndarray | list
NumericalTypes = int | float | np.dtype | jnp.dtype
TupleFloatType = tuple[float, ...]
TupleIntType = tuple[int, ...]
TupleNumericalType = tuple[NumericalTypes, ...]
PackageArrayType = Literal["qutip", "jax", "numpy", "list", "tuple"] | TupleIntType
ModuleType = types.ModuleType


class PielBaseModel(pydantic.BaseModel):
    """
    A base model class that serves as the foundation for other measurement in the project.
    This class extends pydantic's BaseModel and includes additional configuration
    settings for strict validation and immutability.

    Attributes:
        Config: A nested class to configure the behavior of the model.
            arbitrary_types_allowed (bool): Allows arbitrary measurement.
            extra (str): Forbids extra attributes not defined in the model.
            validate_assignment (bool): Validates fields on assignment.
            strict (bool): Enforces strict type validation.
            allow_mutation (bool): Prevents mutation of the model's fields.

    Methods:
        supplied_parameters() -> list[str]:
            Returns a list of parameter names that have been supplied (i.e., are not None).
    """

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
        validate_assignment = True
        strict = True
