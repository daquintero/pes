from ..file_system import return_path
from ..project_structure import get_module_folder_type_location
from ..tools.amaranth import (
    construct_amaranth_module_from_truth_table,
    generate_verilog_from_amaranth_truth_table,
    verify_amaranth_truth_table,
)
from ..types import (
    ElectronicCircuitComponent,
    CircuitComponent,
    HDLSimulator,
    LogicSignalsList,
    PathTypes,
    TruthTable,
)
from piel.conversion import convert_dataframe_to_bits
from ..tools.cocotb import (
    configure_cocotb_simulation,
    run_cocotb_simulation,
    read_simulation_data,
    get_simulation_output_files_from_design,
)
from ..integration.amaranth_openlane import layout_truth_table_through_openlane
from ..integration.gdsfactory_openlane import create_gdsfactory_component_from_openlane


def generate_verilog_and_verification_from_truth_table(
    module: PathTypes,
    truth_table: TruthTable,
    target_file_name: str = "truth_table_module",
):
    """
    Processes a truth table to generate an Amaranth module, converts it to Verilog,
    and creates a testbench for verification.

    Parameters:
    - truth_table (dict): The truth table defining the logic. It should be a dictionary where keys are
                          port names and values are lists of binary strings representing the truth table entries.
                          Example: {"detector_in": ["00", "01", "10", "11"], "phase_map_out": ["00", "10", "11", "11"]}
    - input_ports (list of str): A list of input port names that correspond to keys in the truth table.
                                 Example: ["detector_in"]
    - output_ports (list of str): A list of output port names that correspond to keys in the truth table.
                                  Example: ["phase_map_out"]
    - module (str): The name or path of the module within the design hierarchy where the generated files
                    will be placed. This is used to determine the file structure and directory paths.
                    Example: "full_flow_demo"
    - target_file_name (str): The verilog and vcd file name.

    Returns:
    - None

    Steps:
    1. Combines the input and output connection into a single list.
    2. Constructs an Amaranth module from the provided truth table.
    3. Determines the appropriate directory and source folder for the design.
    4. Generates a Verilog file from the Amaranth module.
    5. Creates a testbench to verify the generated module logic and produces a VCD file.
    """

    # Combine input and output connection into a single list for connection

    # Construct Amaranth module from the truth table
    amaranth_module = construct_amaranth_module_from_truth_table(
        truth_table=truth_table
    )

    # Determine the design directory
    src_folder = get_module_folder_type_location(
        module=module, folder_type="digital_source"
    )

    # Generate Verilog file from the Amaranth module
    generate_verilog_from_amaranth_truth_table(
        amaranth_module=amaranth_module,
        truth_table=truth_table,
        target_file_name=f"{target_file_name}.v",
        target_directory=src_folder,
    )

    # Create a testbench to verify the logic and generate a VCD file
    verify_amaranth_truth_table(
        truth_table_amaranth_module=amaranth_module,
        truth_table=truth_table,
        vcd_file_name=f"{target_file_name}.vcd",
        target_directory=module,
    )


def layout_truth_table(
    truth_table: TruthTable,
    module: PathTypes,
) -> ElectronicCircuitComponent:
    """
    Layout a truth table through the OpenLane flow and create a GDSFactory component.

    Parameters:
    - truth_table (TruthTable): The truth table object containing the input and output port files.
    - module (str): The name or path of the module within the design hierarchy where the generated files
                    will be placed. This is used to determine the file structure and directory paths.
                    Example: "full_flow_demo"

    Returns:
    - digital_component (gf.Component): The GDSFactory component representing the layout of the truth table as implemented by OpenLane
    """
    layout_truth_table_through_openlane(
        truth_table=truth_table,
        parent_directory=module,
        openlane_version="v2",
    )
    digital_component = create_gdsfactory_component_from_openlane(
        design_directory=module
    )
    return digital_component


def read_simulation_data_to_truth_table(
    file_path: PathTypes,
    input_ports: LogicSignalsList,
    output_ports: LogicSignalsList,
    *args,
    **kwargs,
) -> TruthTable:
    """
    The goal of this function is to read an existing simulation files output from cocotb and convert it into a valid Dataframe with proper type validation of bit signals into the corresponding byte formats.

    Args:
    - file_path (PathTypes): The path to the simulation files file.
    - input_ports (LogicSignalsList): The list of input port names.
    - output_ports (LogicSignalsList): The list of output port names.

    Returns:
    - truth_table (TruthTable): The truth table object containing the input and output port files.

    Examples:
    >>> read_simulation_data_to_truth_table("simulation_data.csv", ["input_port"], ["output_port"])
    TruthTable(input_ports=["input_port"], output_ports=["output_port"], ...)
    """
    # Combine input and output connection into a single list for connection
    ports_list = input_ports + output_ports
    # Read the simulation files from the file
    simulation_dataframe = read_simulation_data(file_path, *args, **kwargs)
    # Convert the integer columns to byte format
    simulation_dataframe = convert_dataframe_to_bits(
        dataframe=simulation_dataframe, ports_list=ports_list
    )
    # Create a TruthTable object from the simulation files
    truth_table = TruthTable(
        input_ports=input_ports,
        output_ports=output_ports,
        **simulation_dataframe.to_dict(),
    )
    return truth_table


def run_verification_simulation_for_design(
    module: PathTypes,
    top_level_verilog_module: str,
    test_python_module: str,
    simulator: HDLSimulator = "icarus",
):
    """
    Configures and runs a Cocotb simulation for a given design module and retrieves the simulation files.
    TODO possibly in the future swap the methodology of running the simulation here.

    Parameters:
    - module (str): The name or path of the module within the design hierarchy where the generated files
                    will be placed. This is used to determine the file structure and directory paths.
                    Example: "full_flow_demo"
    - top_level_verilog_module (str): The name of the top-level Verilog module in the design.
                                        Example: "full_flow_demo_module"
    - test_python_module (str): The name of the Python test module for the design.
                                Example: "test_full_flow_demo"
    - simulator (HDLSimulator): The simulator to use for the Cocotb simulation. Default is "icarus".

    Returns:
    - example_simulation_data: The simulation files read from the output files.
    """

    # Determine the design directory and output directories
    design_directory = return_path(module)

    # Configure the Cocotb simulation
    configure_cocotb_simulation(
        design_directory=module,
        simulator=simulator,
        top_level_language="verilog",
        top_level_verilog_module=top_level_verilog_module,
        test_python_module=test_python_module,
        design_sources_list=list((design_directory / "src").iterdir()),
    )

    # Run the Cocotb simulation
    run_cocotb_simulation(design_directory)

    # Retrieve the simulation output files
    cocotb_simulation_output_files = get_simulation_output_files_from_design(module)

    # Read the simulation files from the first output file
    simulation_data = read_simulation_data(cocotb_simulation_output_files[0])

    return simulation_data


def get_latest_digital_run_component(
    module: PathTypes, *args, **kwargs
) -> CircuitComponent:
    component = create_gdsfactory_component_from_openlane(
        design_directory=module, *args, **kwargs
    )
    return component
