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
  toModuleName = builtins.replaceStrings [ "-" ] [ "_" ];
  moduleName = toModuleName finalAttrs.pname;
  pythonPropagatedBuildInputs = [
    annotated-types
    cuda-redist-lib
    pydantic
  ];
  finalAttrs = {
    pname = "cuda-redist-feature-detector";
    version = "0.1.0";
    format = "pyproject";
    src = lib.sources.sourceByRegex ./. [
      "${moduleName}(:?/.*)?"
      "pyproject.toml"
    ];
    nativeBuildInputs = [ flit-core ];
    propagatedBuildInputs = pythonPropagatedBuildInputs;
    pythonImportsCheck =
      builtins.map (drv: toModuleName drv.pname)
        # Check all python propagated build inputs and the package itself
        (pythonPropagatedBuildInputs ++ [ finalAttrs ]);
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
