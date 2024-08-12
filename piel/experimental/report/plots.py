from ...types import PathTypes
from ...file_system import return_path
from ..types import ExperimentData
from ..measurements.extract import load_experiment_data_from_directory


def create_plots_from_experiment_data(
    experiment_data: ExperimentData,
    plot_output_directory: PathTypes = None,
    experiment_directory: PathTypes = None,
) -> list[tuple]:
    """
    This function iterates through all the saved experimental data and generates the corresponding plots
    for the type of data provided using a method as specified.

    Returns a list of (Figures,Axes)
    """
    # First we need to validate an experiment directory does exist. TODO decide if this stays.
    if experiment_directory is None:
        try:
            assert experiment_data.experiment.parent_directory is not None
            assert experiment_data.experiment.parent_directory.exists()
            experiment_directory = experiment_data.experiment.parent_directory
        except Exception as e:
            print("experiment_directory needs to be specified.")
            raise e
    else:
        experiment_directory = return_path(experiment_directory)
    print(f"Experiment data will be extracted from: {experiment_directory}")

    # First we need to validate we have all the configuration required to generate the plots
    if plot_output_directory is None:
        if experiment_directory is None:
            try:
                assert experiment_data.experiment.parent_directory is not None
                assert experiment_data.experiment.parent_directory.exists()
                plot_output_directory = (
                    experiment_data.experiment.parent_directory / "img"
                )
            except Exception as e:
                print("plot_output_directory needs to be specified.")
                raise e
    else:
        plot_output_directory = return_path(plot_output_directory)
    print(f"Plots will be generated at: {plot_output_directory}")

    # Now we need to iterate through each MeasurementData and generate the plot accordingly.

    # TODO implement automatic plot generation here from ExperimentData.
    return experiment_data


def create_plots_from_experiment_directory(
    experiment_directory: PathTypes, plot_output_directory: PathTypes = None, **kwargs
) -> list[tuple]:
    """
    This function will create the plots from the given experiment directory. It will first extract the `ExperimentData`
     from the directory and then generate the plots based on that.
    """
    experiment_directory = return_path(experiment_directory)
    experiment_data = load_experiment_data_from_directory(experiment_directory)
    figure_axes_list = create_plots_from_experiment_data(
        experiment_data=experiment_data, plot_output_directory=plot_output_directory
    )
    return figure_axes_list
