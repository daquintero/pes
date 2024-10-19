import glob
import json
import os
import sys
import pathlib
import shutil
import stat
import subprocess
import types
from typing import Optional
from piel.types import PathTypes, ProjectType, PielBaseModel

__all__ = [
    "check_path_exists",
    "check_example_design",
    "copy_source_folder",
    "copy_example_design",
    "create_new_directory",
    "create_piel_home_directory",
    "delete_path",
    "delete_path_list_in_directory",
    "get_files_recursively_in_directory",
    "get_top_level_script_directory",
    "get_id_map_directory_dictionary",
    "list_prefix_match_directories",
    "permit_directory_all",
    "permit_script_execution",
    "read_json",
    "rename_file",
    "rename_files_in_directory",
    "replace_string_in_file",
    "replace_string_in_directory_files",
    "return_path",
    "rp",
    "run_script",
    "write_file",
    "write_model_to_json",
]


def check_path_exists(
    path: PathTypes,
    raise_errors: bool = False,
) -> bool:
    """
    Checks if a directory exists.

    Args:
        path(PathTypes): Input path.

    Returns:
        directory_exists(bool): True if directory exists.
    """
    directory_exists = False
    path = return_path(path)
    if path.exists():
        directory_exists = True
    else:
        if raise_errors:
            raise ValueError("Path: " + str(path) + " does not exist.")
    return directory_exists


def check_example_design(
    design_name: str = "simple_design",
    designs_directory: PathTypes | None = None,
) -> bool:
    """
    We copy the example simple_design from docs to the `/foss/designs` in the `iic-osic-tools` environment.

    Args:
        design_name(str): Name of the design to check.
        designs_directory(PathTypes): Directory that contains the DESIGNS environment flag.
        # TODO

    Returns:
        None
    """
    if designs_directory is None:
        designs_directory = pathlib.Path(os.environ["DESIGNS"])

    design_folder = (
        designs_directory / design_name
    )  # TODO verify this copying operation
    return design_folder.exists()


def copy_source_folder(
    source_directory: PathTypes,
    target_directory: PathTypes,
    delete: bool = None,
) -> None:
    """
    Copies the files from a source_directory to a target_directory

    Args:
        source_directory(PathTypes): Source directory.
        target_directory(PathTypes): Target directory.
        delete(bool): Delete target directory. Default: False.

    Returns:
        None
    """
    source_directory = return_path(source_directory)
    target_directory = return_path(target_directory)

    if source_directory == target_directory:
        print(
            Warning(
                f"source_directory: {source_directory} and target_directory: {target_directory} cannot be the same."
            )
        )
        return

    if delete is True:
        shutil.rmtree(target_directory)
    else:
        if target_directory.exists():
            answer = input("Confirm deletion of: " + str(target_directory.resolve()))
            if answer.upper() in ["Y", "YES"]:
                shutil.rmtree(target_directory)
            elif answer.upper() in ["N", "NO"]:
                print(
                    "Copying files now from: "
                    + str(source_directory.resolve())
                    + " to "
                    + str(target_directory.resolve())
                )

    shutil.copytree(
        source_directory,
        target_directory,
        symlinks=False,
        ignore=None,
        copy_function=shutil.copy2,
        ignore_dangling_symlinks=False,
        dirs_exist_ok=False,
    )


def copy_example_design(
    project_source: ProjectType = "piel",
    example_name: str = "simple_design",
    target_directory: PathTypes = None,
    target_project_name: Optional[str] = None,
    **kwargs,
) -> None:
    """
    We copy the example simple_design from docs to the `/foss/designs` in the `iic-osic-tools` environment.

    Args:
        project_source(str): Source of the project.
        example_name(str): Name of the example design.
        target_directory(PathTypes): Target directory.
        target_project_name(str): Name of the target project.

    Returns:
        None
    """
    if project_source == "piel":
        example_design_folder = (
            os.environ["PIEL_PACKAGE_DIRECTORY"]
            + "/docs/examples/designs/"
            + example_name
        )
    elif project_source == "openlane":
        import openlane

        example_design_folder = (
            pathlib.Path(openlane.__file__).parent.resolve() / example_name
        )
        design_folder = os.environ["DESIGNS"] + "/" + example_name
    else:
        raise ValueError("project_source must be either 'piel' or 'openlane'.")

    if target_directory is not None:
        target_directory = return_path(target_directory)
        if target_project_name is not None:
            design_folder = target_directory / target_project_name
        else:
            design_folder = target_directory
    else:
        # Copy default openlane example
        design_folder = os.environ["DESIGNS"] + "/" + example_name

    copy_source_folder(
        source_directory=example_design_folder, target_directory=design_folder, **kwargs
    )

    if target_project_name is not None:
        rename_files_in_directory(
            target_directory=design_folder,
            match_string=example_name,
            renamed_string=target_project_name,
        )
        replace_string_in_directory_files(
            target_directory=design_folder,
            match_string=example_name,
            replace_string=target_project_name,
        )


def convert_list_to_path_list(
    input_list: list[PathTypes],
) -> list[pathlib.Path]:
    """
    Converts a list of strings or pathlib.Path to a list of pathlib.Path.

    Args:
        input_list(list[PathTypes]): Input list.

    Returns:
        output_list(list[pathlib.Path]): Output list.
    """
    output_list = []
    for item in input_list:
        item = return_path(item)
        output_list.append(item)
    return output_list


def create_new_directory(
    directory_path: str | pathlib.Path,
    overwrite: bool = False,
) -> bool:
    """
    Creates a new directory.

    If the parents of the target_directory do not exist, they will be created too.

    Args:
        overwrite: Overwrite directory if it already exists.
        directory_path(str | pathlib.Path): Input path.

    Returns:
        None
    """
    directory_path = return_path(directory_path)

    if directory_path.exists():
        if overwrite:
            delete_path(directory_path)
        else:
            return False

    # Check permissions of the parent to be able to create the directory
    parent_directory = directory_path.parent
    parent_directory_permissions = oct(parent_directory.stat().st_mode)

    # If permissions are not read, write and execute for all, we change them
    if parent_directory_permissions != "0o777":
        permit_directory_all(parent_directory)

    # Create the directory
    directory_path.mkdir(parents=True)
    return True


def create_piel_home_directory() -> None:
    """
    Creates the piel home directory.

    Returns:
        None
    """
    # TODO implement check so it does not overwrite.
    piel_home_directory = pathlib.Path.home() / ".piel"
    create_new_directory(piel_home_directory)


def delete_path(path: str | pathlib.Path) -> None:
    """
    Deletes a path.

    Args:
        path(str | pathlib.Path): Input path.

    Returns:
        None
    """
    path = return_path(path)
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()


def delete_path_list_in_directory(
    directory_path: PathTypes,
    path_list: list,
    ignore_confirmation: bool = False,
    validate_individual: bool = False,
) -> None:
    """
    Deletes a list of files in a directory.

    Usage:

    ```python
    delete_path_list_in_directory(
        directory_path=directory_path, path_list=path_list, ignore_confirmation=True
    )
    ```

    Args:
        directory_path(PathTypes): Input path.
        path_list(list): List of files.
        ignore_confirmation(bool): Ignore confirmation. Default: False.
        validate_individual(bool): Validate individual files. Default: False.

    Returns:
        None
    """
    directory_path = return_path(directory_path)
    path_list = convert_list_to_path_list(path_list)
    if validate_individual:
        if ignore_confirmation:
            for path in path_list:
                if path.exists():
                    delete_path(path)
        else:
            for path in path_list:
                if path.exists():
                    answer = input("Confirm deletion of: " + str(path))
                    if answer.upper() in ["Y", "YES"]:
                        delete_path(path)
                    elif answer.upper() in ["N", "NO"]:
                        print("Skipping deletion of: " + str(path))
    else:
        if ignore_confirmation:
            for path in path_list:
                if path.exists():
                    delete_path(path)
        else:
            answer = input("Confirm deletion of: " + str(path_list))
            if answer.upper() in ["Y", "YES"]:
                for path in path_list:
                    if path.exists():
                        delete_path(path)
            elif answer.upper() in ["N", "NO"]:
                print("Skipping deletion of: " + str(path_list))


def get_files_recursively_in_directory(
    path: PathTypes,
    extension: str = "*",
):
    """
    Returns a list of files in a directory.

    Usage:

        get_files_recursively_in_directory('path/to/directory', 'extension')

    Args:
        path(PathTypes): Input path.
        extension(str): File extension.

    Returns:
        file_list(list): List of files.
    """
    path = return_path(path)
    file_list = []
    for x in os.walk(str(path.resolve())):
        for file_path in glob.glob(os.path.join(x[0], f"*.{extension}")):
            file_list.append(file_path)
    return file_list


def get_id_map_directory_dictionary(path_list: list[PathTypes], target_prefix: str):
    """
    Returns a dictionary of ids to directories.

    Usage:

        get_id_to_directory_dictionary(path_list, target_prefix)

    Args:
        path_list(list[PathTypes]): List of paths.
        target_prefix(str): Target prefix.

    Returns:
        id_dict(dict): Dictionary of ids to directories.
    """
    id_dict = {}
    for path in path_list:
        basename = os.path.basename(path)
        # Check if the basename starts with the provided prefix
        if basename.startswith(target_prefix):
            # Extract the id after the prefix
            id_str = basename[len(target_prefix) :]
            # Convert the id string into an integer and use it as a key for the dictionary
            id_dict[int(id_str)] = path
    return id_dict


def get_top_level_script_directory() -> pathlib.Path:
    """
    Attempts to return the top-level script directory when this file is run,
    compatible with various execution environments like Jupyter Lab, pytest, PDM, etc.
    TODO run full verification.

    Returns:
        top_level_script_directory(pathlib.Path): Top level script directory.
    """

    # For Jupyter notebooks and IPython environments
    if "ipykernel" in sys.modules or "IPython" in sys.modules:
        try:
            from IPython.core.getipython import get_ipython

            # IPython's get_ipython function provides access to the IPython interactive environment
            ipython = get_ipython()
            if ipython and hasattr(ipython, "starting_dir"):
                return pathlib.Path(ipython.starting_dir).resolve()
        except Exception as e:
            # Log or print the error as needed
            print(f"Could not determine the notebook directory due to: {e}")

    # For pytest, PDM, and similar environments where sys.argv might be manipulated
    # or __main__.__file__ is not set as expected.
    if "pytest" in sys.modules or "_pytest" in sys.modules or "pdm" in sys.modules:
        return pathlib.Path.cwd()

    # For standard script executions and other environments
    # This checks if __main__ module has __file__ attribute and uses it
    main_module = sys.modules.get("__main__", None)
    if main_module and hasattr(main_module, "__file__"):
        main_file = main_module.__file__
        return pathlib.Path(main_file).resolve().parent

    # As a general fallback, use the current working directory
    return pathlib.Path.cwd()


def list_prefix_match_directories(
    output_directory: PathTypes,
    target_prefix: str,
):
    """
    Returns a list of directories that match a prefix.

    Usage:

        list_prefix_match_directories('path/to/directory', 'prefix')

    Args:
        output_directory(PathTypes): Output directory.
        target_prefix(str): Target prefix.

    Returns:
        matching_dirs(list): List of directories.
    """
    output_directory = return_path(output_directory)
    # Use os.path.join to ensure the path is constructed correctly
    # irrespective of the operating system
    search_path = os.path.join(output_directory, target_prefix + "*")

    # Use glob to get all matching directories
    matching_directories = [d for d in glob.glob(search_path) if os.path.isdir(d)]

    return matching_directories


def permit_script_execution(script_path: PathTypes) -> None:
    """
    Permits the execution of a script.

    Usage:

        permit_script_execution('path/to/script')

    Args:
        script_path(PathTypes): Script path.

    Returns:
        None
    """
    script = return_path(script_path)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)


def permit_directory_all(directory_path: PathTypes) -> None:
    """
    Permits a directory to be read, written and executed. Use with care as it can be a source for security issues.

    Usage:

        permit_directory_all('path/to/directory')

    Args:
        directory_path(PathTypes): Input path.

    Returns:
        None
    """
    directory_path = return_path(directory_path)
    try:
        directory_path.chmod(0o777)
    except PermissionError:
        print(
            UserWarning(
                "Could not change permissions of directory: "
                + str(directory_path.resolve())
                + " to 777. Your Python executable might not have the required permissions. Restructure your project directory so Python does not have to change permissions."
            )
        )


def read_json(path: PathTypes) -> dict:
    """
    Reads a JSON file.

    Usage:

        read_json('path/to/file.json')

    Args:
        path(PathTypes): Input path.

    Returns:
        json_data(dict): JSON files.
    """
    path = return_path(path)
    with open(path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def rename_file(
    match_file_path: PathTypes,
    renamed_file_path: PathTypes,
) -> None:
    """
    Renames a file.

    Usage:

        rename_file('path/to/match_file', 'path/to/renamed_file')

    Args:
        match_file_path(PathTypes): Input path.
        renamed_file_path(PathTypes): Input path.

    Returns:
        None
    """
    match_file_path = return_path(match_file_path)
    renamed_file_path = return_path(renamed_file_path)
    match_file_path.rename(renamed_file_path)


def rename_files_in_directory(
    target_directory: PathTypes,
    match_string: str,
    renamed_string: str,
) -> None:
    """
    Renames all files in a directory.

    Usage:

        rename_files_in_directory('path/to/directory', 'match_string', 'renamed_string')

    Args:
        target_directory(PathTypes): Input path.
        match_string(str): String to match.
        renamed_string(str): String to replace.

    Returns:
        None
    """
    target_directory = return_path(target_directory)
    for path in target_directory.iterdir():
        if path.is_file():
            new_filename = path.name.replace(match_string, renamed_string)
            new_path = path.with_name(new_filename)
            rename_file(path, new_path)


def replace_string_in_file(
    file_path: PathTypes,
    match_string: str,
    replace_string: str,
):
    """
    Replaces a string in a file.

    Usage:

        replace_string_in_file('path/to/file', 'match_string', 'replace_string')

    Args:
        file_path(PathTypes): Input path.
        match_string(str): String to match.
        replace_string(str): String to replace.

    Returns:
        None
    """
    file_path = return_path(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            content = content.replace(match_string, replace_string)

            with file_path.open("w") as file_write:
                file_write.write(content)

    except (UnicodeDecodeError, OSError):
        pass


def replace_string_in_directory_files(
    target_directory: PathTypes,
    match_string: str,
    replace_string: str,
):
    """
    Replaces a string in all files in a directory.

    Usage:

        replace_string_in_directory_files('path/to/directory', 'match_string', 'replace_string')

    Args:
        target_directory(PathTypes): Input path.
        match_string(str): String to match.
        replace_string(str): String to replace.

    Returns:
        None
    """
    target_directory = return_path(target_directory)
    for path in target_directory.rglob("*"):
        if path.is_file():
            replace_string_in_file(path, match_string, replace_string)


def return_path(
    input_path: PathTypes,
    as_piel_module: bool = False,
) -> pathlib.Path:
    """
    Returns a pathlib.Path to be able to perform operations accordingly internally.

    This allows us to maintain compatibility between POSIX and Windows systems. When the `as_piel_module` flag is
    enabled, it will analyse whether the input path can be treated as a piel module, and treat the returned path as a
    module would be treated. This comes useful when analysing files generated in this particular structure accordingly.

    Usage:

        return_path('path/to/file')

    Args:
        input_path(str): Input path.

    Returns:
        pathlib.Path: Pathlib path.
    """

    def treat_as_module(input_path_i: pathlib.Path):
        """
        This function is useful after the path has been converted accordingly. It will analyse whether the path can
        be treated as a module, and return the path to the module accordingly. If it cannot be treated as a piel
        module, then it will return the original path.

        Args:
            input_path_i(pathlib.Path): Input path.

        Returns:
            pathlib.Path: Pathlib path.
        """

        def verify_install_file(install_file_path: pathlib.Path):
            if install_file_path.exists():
                if (input_path_i / directory_name).exists():
                    return input_path_i / directory_name
                else:
                    return input_path_i
            else:
                raise ValueError(
                    "input_path: "
                    + str(input_path_i)
                    + " cannot be treated as a piel module."
                )

        directory_name = input_path_i.name
        try:
            setup_py_path = input_path_i / "setup.py"
            module_directory = verify_install_file(setup_py_path)
        except ValueError:
            input_path_parent_setup_py_path = input_path_i.parent / "setup.py"
            module_directory = verify_install_file(input_path_parent_setup_py_path)
        return module_directory

    if isinstance(input_path, str):
        output_path = pathlib.Path(input_path)
        if as_piel_module:
            output_path = treat_as_module(output_path)
    elif isinstance(input_path, pathlib.Path):
        output_path = input_path
        if as_piel_module:
            output_path = treat_as_module(output_path)
    elif isinstance(input_path, types.ModuleType):
        try:
            output_path = pathlib.Path(input_path.__file__) / ".."
        except Exception:
            # TODO FIX this hacked af
            output_path = pathlib.Path(input_path.__path__[0])
            pass
    elif isinstance(input_path, os.PathLike):
        output_path = pathlib.Path(input_path)
        if as_piel_module:
            output_path = treat_as_module(output_path)
    else:
        raise ValueError(
            "input_path: " + str(input_path) + " is of type: " + str(type(input_path))
        )
    output_path = output_path.resolve()
    return output_path


rp = return_path


def run_script(
    script_path: PathTypes,
    program: str = None,
) -> None:
    """
    Runs a script on the filesystem `script_path`. By default this is a bash script.

    Args:
        script_path(PathTypes): Script path.

    Returns:
        None
    """
    script = return_path(script_path)
    try:
        if program is None:
            subprocess.run(str(script.resolve()), check=True, capture_output=True)
        else:
            subprocess.run(
                [program, str(script.resolve())], check=True, capture_output=True
            )
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script}:")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        raise e  # Re-raise the exception after logging the details


def write_file(
    directory_path: PathTypes,
    file_text: str,
    file_name: str,
    append: bool = False,
) -> bool:
    """
    Writes a file to a directory. Appends to the file if it exists and append is True.

    Args:
        directory_path(PathTypes): Directory path.
        file_text(str): File text.
        file_name(str): File name.
        append(bool): If True, appends to the file if it exists. Defaults to False.

    Returns:
        bool: True if successful.
    """
    directory_path = return_path(directory_path)
    directory_exists = check_path_exists(directory_path)

    if not directory_exists:
        try:
            create_new_directory(directory_path)
        except PermissionError:
            print(
                UserWarning(
                    "Could not create directory: "
                    + str(directory_path.resolve())
                    + ". Your Python executable might not have the required permissions. Restructure your project "
                    "directory so Python does not have to change permissions."
                )
            )
            return False

    mode = (
        "a" if append else "w"
    )  # Use append mode if append is True, otherwise use write mode
    with open(str(directory_path / file_name), mode) as file:
        file.write(file_text)

    return True


def write_model_to_json(
    model: PielBaseModel,
    file_path: PathTypes,
):
    """
    Writes a pydantic model to a JSON file.
    """
    file_path = return_path(file_path)
    with open(file_path, "w") as file:
        json.dump(model.model_dump(), file, indent=4)
    return file_path
