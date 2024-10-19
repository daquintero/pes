import platform
import click
from .main import main


@click.command(
    name="activate",
    help="Provides a command to activate the specific piel nix environment.",
)
def activate_shell():
    """
    Enters the custom piel nix environment with all the supported tools installed and configured packages.
    Runs the nix-shell command on the piel/environment/nix/ directory.
    """
    if platform.system() == "Windows":
        raise NotImplementedError(
            "This installation method is not supported on Windows."
        )
    elif platform.system() == "Darwin":
        raise NotImplementedError("This installation method is not supported on macOS.")
    elif platform.system() == "Linux":
        # Setup the nix shell environment
        print("cd ~/<your_piel_installation_directory>/")
        nix_command = "nix develop . "
        print("Please run this in your shell:")
        print(nix_command)


@click.command(
    name="activate-custom-shell",
    help="Provides a command to activate an extensible custom piel nix shell environment.",
)
def activate_shell():
    """
    Enters the custom piel nix environment with all the supported tools installed and configured packages.
    Runs the nix-shell command on the piel/environment/nix/ directory.
    """
    if platform.system() == "Windows":
        raise NotImplementedError(
            "This installation method is not supported on Windows."
        )
    elif platform.system() == "Darwin":
        raise NotImplementedError("This installation method is not supported on macOS.")
    elif platform.system() == "Linux":
        # Setup the nix shell environment
        print("cd ~/<your_piel_installation_directory>/")
        nix_command = (
            "nix shell . "
            "github:efabless/nix-eda#{ngspice,xschem,verilator,yosys} "
            "github:efabless/openlane2 "
            "nixpkgs#verilog "
            "nixpkgs#gtkwave"
        )
        print("Please run this in your shell:")
        print(nix_command)


main.add_command(activate)
main.add_command(activate_shell)
