import pytest
import subprocess
import types
import json

import piel.project_structure
from piel.project_structure import (
    create_empty_piel_project,
    get_module_folder_type_location,
    pip_install_local_module,
    read_configuration,
)  # Adjust the import based on your actual module structure


# Helper function to create a dummy module
def create_dummy_module(tmp_path):
    module_dir = tmp_path / "dummy_module"
    piel.project_structure.create_empty_piel_project(module_dir)
    return module_dir


# TODO fix this
# # Tests for create_setup_py function
# def test_create_setup_py_from_config_json(tmp_path):
#     design_dir = tmp_path / "design"
#     design_dir.mkdir()
#     config_data = {
#         "NAME": "test_project",
#         "VERSION": "0.1.0",
#         "DESCRIPTION": "A test project for unit testing."
#     }
#     config_path = design_dir / "config.json"
#     with config_path.open("w") as f:
#         json.dump(config_data, f)
#
#     create_setup_py(design_dir)
#
#     setup_path = design_dir / "setup.py"
#     assert setup_path.exists()
#
#     with setup_path.open("r") as f:
#         content = f.read()
#         assert "name='test_project'" in content
#         assert "version=0.1.0" in content
#         assert "description='A test project for unit testing.'" in content


# TODO fix this
# def test_create_setup_py_without_config_json(tmp_path):
#     design_dir = tmp_path / "design"
#     design_dir.mkdir()
#
#     create_setup_py(design_dir, project_name="custom_project", from_config_json=False)
#
#     setup_path = design_dir / "setup.py"
#     assert setup_path.exists()
#
#     with setup_path.open("r") as f:
#         content = f.read()
#         assert "name='custom_project'" in content
#         assert "version='0.0.1'" in content
#         assert "description='Example empty piel project.'" in content


# Tests for create_empty_piel_project function
def test_create_empty_piel_project(tmp_path):
    project_name = "test_project"
    create_empty_piel_project(project_name, tmp_path)

    project_dir = tmp_path / project_name
    assert project_dir.exists()
    assert (project_dir / "docs").exists()
    assert (project_dir / project_name / "io").exists()
    assert (project_dir / project_name / "analogue").exists()
    assert (project_dir / project_name / "components").exists()
    assert (project_dir / project_name / "components" / "analogue").exists()
    assert (project_dir / project_name / "components" / "photonics").exists()
    assert (project_dir / project_name / "components" / "digital").exists()
    assert (project_dir / project_name / "measurement").exists()
    assert (project_dir / project_name / "measurement" / "analogue").exists()
    assert (project_dir / project_name / "measurement" / "frequency").exists()
    assert (project_dir / project_name / "measurement" / "logic").exists()
    assert (project_dir / project_name / "measurement" / "physical").exists()
    assert (project_dir / project_name / "measurement" / "transient").exists()
    assert (project_dir / project_name / "photonic").exists()
    assert (project_dir / project_name / "runs").exists()
    assert (project_dir / project_name / "scripts").exists()
    assert (project_dir / project_name / "sdc").exists()
    assert (project_dir / project_name / "src").exists()
    assert (project_dir / project_name / "tb").exists()
    assert (project_dir / project_name / "tb" / "out").exists()
    assert (project_dir / project_name / "__init__.py").exists()
    assert (project_dir / project_name / "analogue" / "__init__.py").exists()


# Tests for get_module_folder_type_location function
def test_get_module_folder_type_location(tmp_path):
    module_dir = create_dummy_module(tmp_path)
    module = types.ModuleType("dummy_module")
    module.__path__ = str(module_dir / "dummy_file.py")

    src_folder = get_module_folder_type_location(module, "digital_source")
    tb_folder = get_module_folder_type_location(module, "digital_testbench")

    assert src_folder == module_dir / "src"
    assert tb_folder == module_dir / "tb"


# Tests for pip_install_local_module function
def test_pip_install_local_module(tmp_path, monkeypatch):
    module_dir = tmp_path / "local_module"
    module_dir.mkdir()
    setup_file = module_dir / "setup.py"
    with setup_file.open("w") as f:
        f.write("from setuptools import setup; setup(name='local_module')")

    def mock_check_call(cmd, *args, **kwargs):
        assert cmd == ["pip", "install", "-e", str(module_dir)]
        return 0

    monkeypatch.setattr(subprocess, "check_call", mock_check_call)

    pip_install_local_module(module_dir)


# Tests for read_configuration function
def test_read_configuration(tmp_path):
    design_dir = tmp_path / "design"
    design_dir.mkdir()
    config_data = {
        "NAME": "test_project",
        "VERSION": "0.1.0",
        "DESCRIPTION": "A test project for unit testing.",
    }
    config_path = design_dir / "config.json"
    with config_path.open("w") as f:
        json.dump(config_data, f)

    config = read_configuration(design_dir)
    assert config == config_data


def test_read_configuration_missing_file(tmp_path):
    design_dir = tmp_path / "design"
    design_dir.mkdir()

    with pytest.raises(ValueError):
        read_configuration(design_dir)
