from piel.types import PathTypes, LogicImplementationType
from piel.file_system import (
    return_path,
    read_json,
    list_prefix_match_directories,
    get_id_map_directory_dictionary,
)
from .utils import find_latest_design_run

__all__ = [
    "get_all_designs_metrics_openlane_v2",
    "read_metrics_openlane_v2",
    "run_openlane_flow",
]


def get_all_designs_metrics_openlane_v2(
    output_directory: PathTypes,
    target_prefix: str,
):
    """
    Returns a dictionary of all the metrics for all the designs in the output directory.

    Usage:

        ```python
        from piel.tools.openlane import get_all_designs_metrics_v2

        metrics = get_all_designs_metrics_v2(
            output_directory="output",
            target_prefix="design",
        )
        ```

    Args:
        output_directory (PathTypes): The path to the output directory.
        target_prefix (str): The prefix of the designs to get the metrics for.

    Returns:
        dict: A dictionary of all the metrics for all the designs in the output directory.
    """
    output_directory = return_path(output_directory)
    designs_directory_list = list_prefix_match_directories(
        output_directory=output_directory,
        target_prefix=target_prefix,
    )
    id_map_directory = get_id_map_directory_dictionary(
        path_list=designs_directory_list,
        target_prefix=target_prefix,
    )
    output_dictionary = dict()
    for id_i, directory_i in id_map_directory.items():
        metrics_dictionary_i = read_metrics_openlane_v2(design_directory=directory_i)
        output_dictionary[id_i] = {
            "directory": directory_i,
            **metrics_dictionary_i,
        }
    return output_dictionary


def read_metrics_openlane_v2(design_directory: PathTypes) -> dict:
    """
    Read design metrics from OpenLane v2 run files.

    Args:
        design_directory(PathTypes): Design directory PATH.

    Returns:
        dict: Metrics dictionary.
    """
    design_directory = return_path(design_directory)
    run_directory, version = find_latest_design_run(
        design_directory=design_directory, version="v2"
    )
    metrics_path = run_directory / "final" / "metrics.json"
    metrics_dictionary = read_json(metrics_path)
    return metrics_dictionary


def generate_flow_setup(
    configuration: dict | None = None,
    design_directory: PathTypes = ".",
    logic_implementation_type: LogicImplementationType = "combinatorial",
):
    from openlane.flows import Flow

    if logic_implementation_type == "combinatorial":
        from openlane.flows import SequentialFlow
        from openlane.steps import Yosys, OpenROAD, Magic, Netgen, Checker

        class DigitalCombinatorialFlow(SequentialFlow):
            Steps = [
                Yosys.Synthesis,
                OpenROAD.CheckSDCFiles,
                OpenROAD.Floorplan,
                OpenROAD.TapEndcapInsertion,
                OpenROAD.GeneratePDN,
                OpenROAD.IOPlacement,
                OpenROAD.GlobalPlacement,
                OpenROAD.RepairDesign,
                OpenROAD.DetailedPlacement,
                OpenROAD.GlobalRouting,
                OpenROAD.DetailedRouting,
                OpenROAD.FillInsertion,
                Magic.StreamOut,
                Magic.DRC,
                Checker.MagicDRC,
                Magic.SpiceExtraction,
                Netgen.LVS,
                Checker.LVS,
            ]

        print(configuration)
        flow = DigitalCombinatorialFlow(
            config=configuration,
            design_dir=str(design_directory.resolve()),
        )
    else:
        Classic = Flow.factory.get("Classic")

        flow = Classic(
            config=configuration,
            design_dir=str(design_directory.resolve()),
        )
    return flow


def run_openlane_flow(
    configuration: dict | None = None,
    design_directory: PathTypes = ".",
    logic_implementation_type: LogicImplementationType = "combinatorial",
    parallel_asynchronous_run: bool = False,
    only_generate_flow_setup: bool = False,
):
    """
    Runs the OpenLane v2 flow, creates a custom configuration according to the type of the digital logic implementation.

    Args:
        configuration(dict): OpenLane configuration dictionary. If none is present it will default to the config.json file on the design_directory.
        design_directory(PathTypes): Design directory PATH.
        parallel_asynchronous_run(bool): Run the flow in parallel.
        only_generate_flow_setup(bool): Only generate the flow setup.
        logic_implementation_type(LogicImplementationType): Type of digital synthesis to determine the openlane build flow.

    Returns:
        Flow

    """
    design_directory = return_path(design_directory)

    try:
        print(configuration)
        flow = generate_flow_setup(
            configuration=configuration,
            design_directory=design_directory,
            logic_implementation_type=logic_implementation_type,
        )

        if configuration is None:
            # Get extract configuration file from config.json on directory
            config_json_filepath = design_directory / "config.json"
            configuration = read_json(str(config_json_filepath.resolve()))

        if not only_generate_flow_setup:
            pass
        else:
            return flow

        if parallel_asynchronous_run:
            # TODO implement
            flow.start()
        else:
            flow.start()

        return flow

    except ModuleNotFoundError as e:
        print(
            f"Make sure you are running this from an environment with Openlane nix installed {e}"
        )
