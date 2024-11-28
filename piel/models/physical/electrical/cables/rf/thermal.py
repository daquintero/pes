from piel.models.physical.thermal import heat_transfer_1d_W
from piel.materials.thermal_conductivity.utils import get_thermal_conductivity_fit
from piel.types.electrical.cables import (
    CoaxialCableGeometryType,
    CoaxialCableHeatTransferType,
    CoaxialCableMaterialSpecificationType,
)
from piel.types.materials import MaterialReferenceType
from piel.types.physical import TemperatureRangeTypes


def calculate_coaxial_cable_heat_transfer(
    temperature_range_K: TemperatureRangeTypes = [273, 293],
    geometry_class: CoaxialCableGeometryType = CoaxialCableGeometryType(),
    material_class: CoaxialCableMaterialSpecificationType | None = None,
    core_material: MaterialReferenceType | None = None,
    sheath_material: MaterialReferenceType | None = None,
    dielectric_material: MaterialReferenceType | None = None,
) -> CoaxialCableHeatTransferType:
    """
    Calculate the heat transfer of a coaxial cable.

    Args:
        temperature_range_K: The temperature range in Kelvin.
        geometry_class: The geometry of the cable.
        material_class: The material of the cable.
        core_material: The material of the core.
        sheath_material: The material of the sheath.
        dielectric_material: The material of the dielectric.

    Returns:
        CoaxialCableHeatTransferType: The heat transfer of the cable.
    """
    if material_class is not None:
        provided_materials = material_class.supplied_parameters()
    elif material_class is None:
        material_class = CoaxialCableMaterialSpecificationType(
            core=core_material, sheath=sheath_material, dielectric=dielectric_material
        )
        provided_materials = material_class.supplied_parameters()
    else:
        raise ValueError("No material class or material parameters provided.")

    heat_transfer_parameters = dict()
    total_heat_transfer_W = 0
    for material_i in provided_materials:
        print(material_i)
        if material_i is None:
            continue
        else:
            thermal_conductivity_fit_i = get_thermal_conductivity_fit(
                temperature_range_K=temperature_range_K,
                material=getattr(material_class, material_i),
            )
            # CURRENT TODO compute the thermal conductivity fit accordingly. Implement a material reference to thermal conductivtiy files mapping.

            heat_transfer_i = heat_transfer_1d_W(
                thermal_conductivity_fit=thermal_conductivity_fit_i,
                temperature_range_K=temperature_range_K,
                cross_sectional_area_m2=geometry_class.total_cross_sectional_area_m2,
                length_m=geometry_class.length_m,
            )
            heat_transfer_parameters[material_i] = heat_transfer_i
            total_heat_transfer_W += heat_transfer_i

    heat_transfer_parameters["total"] = total_heat_transfer_W

    return CoaxialCableHeatTransferType(
        **heat_transfer_parameters,
    )
