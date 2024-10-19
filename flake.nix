{
  description = "Python application packaged using poetry2nix and additional EDA tools";

  inputs = {
    nixpkgs.url    = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    nix-eda.url    = "github:efabless/nix-eda";
    openlane2.url  = "github:efabless/openlane2";
  };

  outputs = { self, nixpkgs, poetry2nix, nix-eda, openlane2 }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      # Correctly accessing nix-eda and openlane2 outputs
      edaPkgs  = nix-eda.packages.${system};
      openlane = openlane2.packages.${system}.openlane; # Verify the exact output name

      # Use the same Python version as OpenLane
      python = pkgs.python311Full;

      # Create a custom "mkPoetryApplication" using poetry2nix
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;

      # Define build requirements for specific Python packages
      pypkgs-build-requirements = {
        rectpack      = [ "setuptools" ];
        vlsir         = [ "setuptools" ];
        vlsirtools    = [ "setuptools" ];
        hdl21         = [ "flit-core" ];
        sky130-hdl21  = [ "flit-core" ];
        gdsfactory    = [ "flit-core" ];
        sky130        = [ "flit-core" ];
        thewalrus     = [ "setuptools" ];
      };

      # Extend default poetry overrides with custom build requirements
      custom_overrides = defaultPoetryOverrides.extend (final: prev:
        builtins.mapAttrs (package: build-requirements:
          (builtins.getAttr package prev).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or []) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg prev else pkg) build-requirements);
          })
        ) pypkgs-build-requirements
      );

      # Define the main application using poetry2nix
      app = mkPoetryApplication {
        projectDir  = ./.;
        preferWheels = true;
        extras      = [];
        overrides   = custom_overrides;
        python      = python;
      };

      # Override the application to include additional build inputs
      overridden = app.overrideAttrs (old: {
        name                = "${old.pname}-overridden-${old.version}";
        nativeBuildInputs   = old.nativeBuildInputs or [] ++ [
          pkgs.python3Packages.hatchling
          pkgs.python3Packages.scikit-build-core
          pkgs.python3Packages.scikit-learn
        ];
        propagatedBuildInputs = old.propagatedBuildInputs or [] ++ [
          pkgs.python3Packages.hatchling
          pkgs.python3Packages.scikit-build-core
          pkgs.python3Packages.scikit-learn
        ];
      });

      # Define a dependency environment
      depEnv = app.dependencyEnv.override {
        app = overridden;
      };

    in
    {
      # Define packages
      packages.${system} = {
        default = app;
        python  = python;
      };

      # Define applications
      apps.${system}.default = {
        type    = "app";
        program = "${app}/bin/piel"; # Ensure 'piel' is the correct entry script
      };

      # Define development shells
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python3Full            # Include Python 3
          app
          edaPkgs.ngspice
          edaPkgs.xschem
          edaPkgs.verilator
          edaPkgs.yosys
          openlane
          pkgs.verilog
          pkgs.gtkwave
          pkgs.uv                     # Added uv to buildInputs
        ];

        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
          ]}
          echo "Setting Piel-Nix Environment Up"
          export PATH=${app}/bin:$PATH
          export PYTHONPATH=${app}/lib/python${python.version}/site-packages:$PYTHONPATH
          alias python=python3          # Alias 'python' to 'python3'
          rm -rf .venv
          python -m venv .venv
          source .venv/bin/activate     # Activate the virtual environment
          echo "Virtual environment activated. Installing additional packages with pip..."
          uv pip install -e .[dev]
          uv pip install -r requirements_notebooks.txt
        '';
        LOCALE_ARCHIVE="/usr/lib/locale/locale-archive";  # let's nix read the LOCALE, to silence warning messages
      };
    };
}
