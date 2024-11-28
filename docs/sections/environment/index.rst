*************
Environment
*************

.. include:: tools_environment.rst

``piel CLI`` (Recommended - CI Tested)
========================================================================

``piel`` is a command line interface (CLI) that is designed to be a simple and easy to use tool for managing the ``piel`` toolchain. It is necessary to first install ``piel`` in a given python environment and then the CLI tool should automatically be active in that environment. You then just need to run ``$ piel`` in the terminal to see the available commands.

.. include:: piel_cli/common_useful_commands.rst

``nix`` Configuration (Recommended - CI Tested)
========================================================================

This is the recommended way to access the entire toolset environment. This will install all the external dependencies such as ``openlane``, ``ngspice``, ``cocotb`` and so on. It can be easily extended in a standard nix-pkgs flow. However, in order to run this flow you need to have nix installed which is feasible in Linux and MacOS. The entire ``piel`` package gets tested in this  `nix environment in the CI <https://github.com/daquintero/piel/blob/develop/.github/workflows/nix_environment_testing.yaml>`_ so it is reproducible to some level.

The quickstart in an ubuntu environment is just the following script. This will install nix with the correct configuration and build the nix-flake correctly. We use this script in the CI.

.. code-block::

    git clone https://github.com/daquintero/piel.git
    source scripts/install_piel_nix.sh


If you just want to enter a nix development environment shell by default and you already have nix installed, then you just have to run:

.. code-block::

    nix develop .

This is the output set of instrructions provided by:

.. code-block::

    piel activate


If you want to enter the corresponding `nix-shell` environment which is extensible with further packages, you can run the following command which will print the updated command you just need to copy paste into your terminal to activate the `nix-shell` environment.

.. code-block:: bash

    $ piel activate-custom-shell

It will print:

.. code-block::

    # Please run this in your shell:
    cd ~/<path_to_piel>
    nix shell . github:efabless/nix-eda#{ngspice,xschem,verilator,yosys} github:efabless/openlane2 nixpkgs#verilog nixpkgs#gtkwave

This is because, I believe, for security reasons it is very difficult to automatically enter a nix shell directly from python or a subprocess.

`OpenLane 2 via nix <https://openlane2.readthedocs.io/en/latest/getting_started/index.html#nix-recommended>`__ have recently released another way to package their `python`-driven ``Openlane 2`` digital chip layout flow. We have previously had issues reproducibly building the `docker` configuration, and because most users are likely to use these tools for developing their chips rather than distributing software, `nix <https://nixos.org/>`__ might be well suited for these applications.

.. include:: nix/development_installation.rst
.. include:: nix/custom_nix_installation.rst
.. include:: nix/relevant_nix_commands.rst
