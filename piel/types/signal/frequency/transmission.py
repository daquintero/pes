from __future__ import annotations
from piel.types.connectivity.abstract import Instance
from piel.types.signal.frequency.sax_core import SType
from piel.types.signal.frequency.generic import PhasorTypes
from piel.types.connectivity.generic import ConnectionTypes
from piel.base.signal.frequency.transmission import get_phasor_length
from pydantic import model_validator
from typing import Any


class PathTransmission(Instance):
    connection: ConnectionTypes
    transmission: PhasorTypes
    """
    A frequency-domain representation of transmission requires the full input response which can be represented
    as an array, an individual value, or a static-typed data structure - as per performance requirements.
    """


class NetworkTransmission(Instance):
    """
    This corresponds to a transmission component or array collection of the power or frequency transmission.
    For example, for the reflected power (ie S11 transmission), this contains magnitude and phase information from a source.
    Instead of responding to a given input. Note that this does not contain mode information, but could
    be extended to implement this.

    This can represent frequency to single-state conversion and a sckit-rf collective model too, based on its definition.

    This implementation is flexible because making the transmission individual is kind of essential when dealing with both electronic-photonic s-parameter state
    management, or otherwise it involves writing a mapping function. This is not the fastest approach, but certainly complete.
    Maybe someone can come up with a more complete approach that is not so resource intensive or we can abstract this into
    defined base-types (but I think this is it though if any validation is to be applied?)

    This can also be equivalent to a sckit-rf Network static data container, just that it decomposes each specific transmission to a given
    frequency or power-point. It implements translation between RF models and Photonic models which are more-port specific
    as defined by SAX. This enables more specific electronic-photonic state mapping.
    """

    input: PhasorTypes
    """
    The combined definition of the input state input with magnitude and phase information.
    Could be extended to a spectral input incidence. The length of the PhasorType should match the length of the
    equivalent PathTransmission for one dimension of the input representation.
    """

    network: list[PathTransmission] = []
    """
    Contains the entire frequency transmission response per component. Can be defined both per state and per full collection.

    TODO implement port mapping already.
    """

    @model_validator(mode="after")
    def check_length_consistency(cls, model):
        input_phasor = model.input
        network = model.network

        input_length = get_phasor_length(
            input_phasor.magnitude
        )  # Assumes the input declaration has been validated already
        # TODO update for non-Phasor input values.

        for idx, path_trans in enumerate(network):
            trans = path_trans.transmission
            trans_length = get_phasor_length(trans)
            if trans_length != input_length:
                raise ValueError(
                    f"Length mismatch at network[{idx}]: transmission length {trans_length} does not match input length {input_length}"
                )

        return model


FrequencyTransmissionModel = NetworkTransmission | SType | Any | None
"""
Corresponds to a container that contains a s-parameter transmission model, for example.

This type alias is currently a placeholder (Any | None).
The idea is that this is a collective static data representation compatible with both a sax-translation as
with the standard sckit-rf network models.
"""

FrequencyTransmissionList = list[FrequencyTransmissionModel]
