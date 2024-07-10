{ lib, python312Packages }:
let
  callPackage = lib.trivial.flip python312Packages.callPackage { };
  toModuleName = builtins.replaceStrings [ "-" ] [ "_" ];
in
callPackage (
  {
    buildPythonPackage,
    lib,
    # nativeBuildInputs
    flit-core,
    # propagatedBuildInputs
    annotated-types,
    pydantic,
    rich,
    # passthru.optional-dependencies.dev
    pyright,
    ruff,
  }:
  let
    moduleName = toModuleName finalAttrs.pname;
    finalAttrs = {
      pname = "cuda-redist-lib";
      version = "0.1.0";
      pyproject = true;
      src = lib.sources.sourceByRegex ./. [
        "${moduleName}(:?/.*)?"
        "pyproject.toml"
      ];
      build-system = [ flit-core ];
      dependencies = [
        annotated-types
        pydantic
        rich
      ];
      pythonImportsCheck = [ moduleName ];
      nativeCheckInputs = [
        pyright
        ruff
      ];
      passthru.optional-dependencies.dev = [
        pyright
        ruff
      ];
      doCheck = true;
      checkPhase =
        # preCheck
        ''
          runHook preCheck
        ''
        # Check with ruff
        + ''
          echo "Linting with ruff"
          ruff check
          echo "Checking format with ruff"
          ruff format --diff
        ''
        # Check with pyright
        + ''
          echo "Typechecking with pyright"
          pyright --warnings
          echo "Verifying type completeness with pyright"
          pyright --verifytypes ${moduleName} --ignoreexternal
        ''
        # postCheck
        + ''
          runHook postCheck
        '';
      meta = with lib; {
        description = "Library of functions for NVIDIA's redistributable manifests";
        homepage = "https://github.com/ConnorBaker/${finalAttrs.pname}";
        maintainers = with maintainers; [ connorbaker ];
      };
    };
  in
  buildPythonPackage finalAttrs
)
