{
  buildPythonPackage,
  lib,
  # nativeBuildInputs
  flit-core,
  # propagatedBuildInputs
  annotated-types,
  click,
  cudaPackages,
  patchelf,
  pydantic_v2,
  rich,
  typing-extensions,
  # passthru.optional-dependencies.dev
  black,
  pyright,
  ruff,
}: let
  toModuleName = builtins.replaceStrings ["-"] ["_"];
  moduleName = toModuleName attrs.pname;
  pythonPropagatedBuildInputs = [
    annotated-types
    click
    pydantic_v2
    rich
    typing-extensions
  ];
  attrs = {
    pname = "cuda-redist-find-features";
    version = "0.1.0";
    format = "pyproject";
    src = lib.sources.sourceByRegex ../.. [
      "${moduleName}(:?/.*)?"
      "pyproject.toml"
    ];
    nativeBuildInputs = [
      flit-core
    ];
    propagatedBuildInputs =
      [
        cudaPackages.cuda_cuobjdump
        patchelf
      ]
      ++ pythonPropagatedBuildInputs;
    pythonImportsCheck =
      builtins.map
      (drv: toModuleName drv.pname)
      # Check all python propagated build inputs and the package itself
      (pythonPropagatedBuildInputs ++ [attrs]);
    passthru.optional-dependencies.dev = [
      black
      pyright
      ruff
    ];
    meta = with lib; {
      description = "Find features provided by a CUDA redistributable";
      homepage = "https://github.com/ConnorBaker/${attrs.pname}";
      maintainers = with maintainers; [connorbaker];
    };
  };
in
  buildPythonPackage attrs
