{ python312Packages }:
let
  callPackage = attrs: python312Packages.callPackage attrs { };
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
    cuda-redist-lib,
    pydantic,
    # passthru.optional-dependencies.dev
    pyright,
    ruff,
  }:
  let
    moduleName = toModuleName finalAttrs.pname;
    finalAttrs = {
      pname = "cuda-redist-feature-detector";
      version = "0.1.0";
      pyproject = true;
      src = lib.sources.sourceByRegex ./. [
        "${moduleName}(:?/.*)?"
        "pyproject.toml"
      ];
      build-system = [ flit-core ];
      dependencies = [
        annotated-types
        cuda-redist-lib
        pydantic
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
        ''
        # postCheck
        + ''
          runHook postCheck
        '';
      meta = with lib; {
        description = "Detects the presence of certain features of a CUDA redistributable given the path of an unpacked tarball";
        homepage = "https://github.com/ConnorBaker/${finalAttrs.pname}";
        maintainers = with maintainers; [ connorbaker ];
      };
    };
  in
  buildPythonPackage finalAttrs
)
