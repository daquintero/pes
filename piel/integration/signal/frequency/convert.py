from piel.types import NetworkTransmission, FrequencyTransmissionModel


def convert_to_network_transmission(
    network: FrequencyTransmissionModel,
) -> NetworkTransmission:
    """
    This function takes in any supported FrequencyTransmissionModel and provides translation between the different
    domain representations and returns a standard NetworkTransmission class.
    """
    import skrf
    from piel.tools.skrf.convert import convert_skrf_network_to_network_transmission

    if isinstance(network, skrf.Network):
        network_transmission = convert_skrf_network_to_network_transmission(network)
    else:
        network_transmission = NetworkTransmission()
    return network_transmission
