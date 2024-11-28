{
  buildPythonPackage,
  lib,
  # nativeBuildInputs
  flit-core,
  makeWrapper,
  # propagatedBuildInputs
  annotated-types,
  click,
  cudaPackages,
  nix,
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
    version = "0.1.1";
    format = "pyproject";
    src = lib.sources.sourceByRegex ../.. [
      "${moduleName}(:?/.*)?"
      "pyproject.toml"
    ];
    nativeBuildInputs = [
      flit-core
      makeWrapper
    ];
    propagatedBuildInputs =
      [
        cudaPackages.cuda_cuobjdump
        nix
        patchelf
      ]
      ++ pythonPropagatedBuildInputs;
    pythonImportsCheck =
      builtins.map
      (drv: toModuleName drv.pname)
      # Check all python propagated build inputs and the package itself
      (pythonPropagatedBuildInputs ++ [finalAttrs]);
    postInstall = ''
      wrapProgram "$out/bin/${finalAttrs.meta.mainProgram}" \
        --prefix PATH : "${
          lib.strings.makeBinPath [
            cudaPackages.cuda_cuobjdump
            nix
            patchelf
          ]
        }"
    '';
    passthru.optional-dependencies.dev = [
      pyright
      ruff
    ];
    meta = with lib; {
      description = "Find features provided by a CUDA redistributable";
      homepage = "https://github.com/ConnorBaker/${finalAttrs.pname}";
      license = licenses.mit;
      maintainers = with maintainers; [connorbaker];
      mainProgram = "cuda-redist-find-features";
    };
  };
in
  buildPythonPackage finalAttrs
