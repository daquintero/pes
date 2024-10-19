import pytest
import os
from subprocess import run, CalledProcessError

import piel


@pytest.fixture(scope="module")
def script_directory():
    return os.environ.get("PIEL_PACKAGE_DIRECTORY")


def test_script_execution(script_directory):
    piel.develop.configure_development_environment()

    scripts = [
        # "00_setup.py", # TODO test in distributed machine when we have a way to install openlane
        # "01_run_openlane_flow.py", # TODO test in distributed machine when we have a way to install openlane
        # "02a_large_scale_digital_layout.py",  # TODO test in machine when we have a way to install openlane
        "03_sax_basics.py",
        "03a_sax_cocotb_cosimulation.py",
        "03b_optical_function_verification.py",
        "04_spice_cosimulation.py",
        "06_component_codesign_basics.py",
    ]

    for script in scripts:
        script_path = os.path.join(script_directory, script)
        try:
            run(
                ["uv", "run", "python", script_path],
                capture_output=True,
                text=True,
                check=True,
            )
        except CalledProcessError as e:
            pytest.fail(
                f"Script {script} failed with return code {e.returncode}, output: {e.output}"
            )


if __name__ == "__main__":
    pytest.main()
