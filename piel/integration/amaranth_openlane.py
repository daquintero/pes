"""
This file enhances some functions that translate an `amaranth` function to an `openlane` flow implementation.
"""

from typing import Optional, Literal
from ..types import PathTypes, TruthTable, DigitalLogicModule


def layout_truth_table_through_openlane(
    truth_table: TruthTable,
    parent_directory: PathTypes,
    target_directory_name: Optional[str] = None,
    openlane_version: Literal["v1", "v2"] = "v2",
    **kwargs,
):
    """
    Translates a truth table to an OpenLane flow implementation.

    This function takes a truth table and converts it into an OpenLane flow, using the specified OpenLane version.
    It first constructs an Amaranth module from the truth table, and then passes this module to the
    `layout_amaranth_truth_table_through_openlane` function for further processing.

    Args:
        truth_table (TruthTable): The truth table to be converted. It includes input connection, output connection, and the table logic.
        parent_directory (PathTypes): The directory where the OpenLane project will be created.
        target_directory_name (Optional[str]): Name of the target directory. If not specified, a default name will be used.
        openlane_version (Literal["v1", "v2"]): Specifies the OpenLane version to use. Defaults to "v2".
        **kwargs: Additional keyword arguments passed to the Amaranth module construction.

    Returns:
        None
    """
    from ..tools.amaranth import (
        construct_amaranth_module_from_truth_table,
    )

    # Extract inputs and outputs from the truth table
    truth_table = truth_table

    # Construct an Amaranth module from the truth table
    our_truth_table_module = construct_amaranth_module_from_truth_table(
        truth_table=truth_table, **kwargs
    )

    # Pass the constructed module to the OpenLane flow layout function
    layout_amaranth_truth_table_through_openlane(
        amaranth_module=our_truth_table_module,
        truth_table=truth_table,
        parent_directory=parent_directory,
        target_directory_name=target_directory_name,
        openlane_version=openlane_version,
        **kwargs,
    )


def layout_amaranth_truth_table_through_openlane(
    amaranth_module: DigitalLogicModule,
    truth_table: TruthTable,
    parent_directory: PathTypes,
    target_directory_name: Optional[str] = None,
    openlane_version: Literal["v1", "v2"] = "v2",
    openlane_configuration: dict | None = None,
    **kwargs,
):
    """
    Implements an Amaranth truth table module through the OpenLane flow.

    This function implements an amaranth truth-table module through the openlane flow. There are several ways to
    implement a module. Fundamentally, this requires the verilog files to be generated from the openlane-module in a
    particular directory. For the particular directory provided, this function will generate the verilog files in the
    corresponding directory. It can also generate the ``openlane`` configuration files for this particular location.

    This function does a few things:

    1. Starts off from a ``amaranth`` module class.
    2. Determines the output directory in which to generate the files, and creates one accordingly if it does not exist.
    3. Generates the verilog files from the ``amaranth`` module class.
    4. Generates the ``openlane`` configuration files for this particular location.
    5. Implements the ``openlane`` flow for this particular location to generate a chip.

    Args:
        amaranth_module (am.Module): The Amaranth module representing the truth table logic.
        truth_table (TruthTable): The truth table files structure containing the logic for the module.
        parent_directory (PathTypes): The directory where the project will be created or found.
        target_directory_name (Optional[str]): The name for the target directory. Defaults to the name of the Amaranth module's class.
        openlane_version (Literal["v1", "v2"]): The version of OpenLane to use. Defaults to "v2".
        **kwargs: Additional keyword arguments for OpenLane configuration.

    Returns:
        None
    """
    import types as ty
    from ..tools.amaranth import (
        generate_verilog_from_amaranth_truth_table,
    )
    from ..file_system import return_path, create_new_directory
    from ..project_structure import create_empty_piel_project
    from ..tools.openlane.v1 import write_configuration_openlane_v1
    from ..tools.openlane.v2 import run_openlane_flow
    from ..tools.openlane.defaults import (
        test_basic_open_lane_configuration_v1,
        test_basic_open_lane_configuration_v2,
    )

    # TODO static typing verification of am.Module

    # Determine the design and source directories
    if isinstance(parent_directory, ty.ModuleType):
        parent_directory = return_path(parent_directory)
        design_directory = parent_directory
        src_folder = parent_directory / "src"
    else:
        parent_directory = return_path(parent_directory)
        if not parent_directory.exists():
            create_new_directory(parent_directory)
        # Create a new project structure if the directory does not exist
        target_directory_name = (
            target_directory_name
            if target_directory_name is not None
            else amaranth_module.__class__.__name__
        )
        create_empty_piel_project(
            project_name=target_directory_name,
            parent_directory=parent_directory,
        )
        design_directory = (
            parent_directory / target_directory_name / target_directory_name
        )
        src_folder = design_directory / "src"

    # Generate the Verilog files from the Amaranth module
    generate_verilog_from_amaranth_truth_table(
        amaranth_module=amaranth_module,
        truth_table=truth_table,
        target_file_name="truth_table_module.v",
        target_directory=src_folder,
    )

    # Configure and run the OpenLane flow based on the specified version
    if openlane_version == "v1":
        if openlane_configuration is None:
            openlane_configuration = test_basic_open_lane_configuration_v1
        write_configuration_openlane_v1(
            configuration=openlane_configuration,
            design_directory=design_directory,
        )
        # TODO: Additional steps for OpenLane v1 configuration

    elif openlane_version == "v2":
        if openlane_configuration is None:
            openlane_configuration = test_basic_open_lane_configuration_v2
        try:
            run_openlane_flow(
                configuration=openlane_configuration,
                design_directory=design_directory,
                **kwargs,
            )
        except ModuleNotFoundError as e:
            print(
                f"Make sure you are running this from an environment with Openlane nix installed {e}"
            )
