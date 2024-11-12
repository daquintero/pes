"""Top-level package for piel."""

import os
import pathlib

# Libraries - Do not change the order
import piel.types as types  # NOQA: F401
import piel.models as models  # NOQA: F401
import piel.units as units  # NOQA: F401
import piel.materials as materials  # NOQA: F401
import piel.tools as tools  # NOQA: F401

# Functions
from piel.file_system import *  # NOQA: F403
from piel.project_structure import *  # NOQA: F403
from piel.utils import *  # NOQA: F403
from piel.connectivity import *  # NOQA: F403

import piel.analysis as analysis  # NOQA: F401
import piel.conversion as conversion  # NOQA: F401
import piel.base as base  # NOQA: F401
import piel.experimental as experimental  # NOQA: F401
import piel.file_system as file_system  # NOQA: F401
import piel.develop as develop  # NOQA: F401
import piel.visual as visual  # NOQA: F401
import piel.integration as integration  # NOQA: F401
import piel.flows as flows  # NOQA: F401

os.environ["PIEL_PACKAGE_DIRECTORY"] = str(
    pathlib.Path(__file__).parent.parent.resolve()
)

create_piel_home_directory()  # NOQA: F405

__author__ = """Dario Quintero"""
__email__ = "darioaquintero@gmail.com"
__version__ = "0.1.0"
