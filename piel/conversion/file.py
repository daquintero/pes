import pandas as pd
from piel.file_system import return_path
from piel.types import PathTypes


def read_csv_to_pandas(file_path: PathTypes):
    """
    This function returns a Pandas dataframe that contains all the simulation files outputted from the simulation run.
    """
    file_path = return_path(file_path)
    simulation_data = pd.read_csv(file_path)
    return simulation_data


def read_vcd_to_json(file_path: PathTypes):
    from pyDigitalWaveTools.vcd.parser import VcdParser

    file_path = return_path(file_path)
    with open(str(file_path.resolve())) as vcd_file:
        vcd = VcdParser()
        vcd.parse(vcd_file)
        json_data = vcd.scope.toJson()
    return json_data
