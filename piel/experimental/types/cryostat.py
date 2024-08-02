from typing import Optional
from ...types import Environment, Component


class TemperatureStage(Environment, Component):
    """
    Standard definition for a generic temperature stage.
    """

    surface_area_m2: Optional[float] = None  # TODO move to a geometry type.


class Cryostat(Component):
    temperature_stages: list[TemperatureStage]
