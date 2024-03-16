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
  pydantic,
  rich,
  typing-extensions,
  # passthru.optional-dependencies.dev
  pyright,
  ruff,
}: let
  toModuleName = builtins.replaceStrings ["-"] ["_"];
  moduleName = toModuleName finalAttrs.pname;
  pythonPropagatedBuildInputs = [
    annotated-types
    click
    pydantic
    rich
    typing-extensions
  ];
  finalAttrs = {
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
      (pythonPropagatedBuildInputs ++ [finalAttrs]);
    passthru.optional-dependencies.dev = [
      pyright
      ruff
    ];
    meta = with lib; {
      description = "Find features provided by a CUDA redistributable";
      homepage = "https://github.com/ConnorBaker/${finalAttrs.pname}";
      maintainers = with maintainers; [connorbaker];
    };
  };
in
  buildPythonPackage finalAttrs
