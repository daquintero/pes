# An example package with dependencies defined via pyproject.toml
{
  config,
  lib,
  dream2nix,
}: let
  pyproject = lib.importTOML (config.mkDerivation.src + ../../pyproject.toml);
in {
  imports = [
    dream2nix.modules.dream2nix.pip
  ];

  inherit (pyproject.project) name version;

  mkDerivation = {
    src = ./.;
  };

  buildPythonPackage = {
    format = lib.mkForce "pyproject";
    pythonImportsCheck = [
      "piel"
    ];
  };

  pip = {
    pypiSnapshotDate = "2023-08-27";
    requirementsList =
      pyproject.build-system.requires
      or []
      ++ pyproject.project.dependencies;
    flattenDependencies = true;
  };
}