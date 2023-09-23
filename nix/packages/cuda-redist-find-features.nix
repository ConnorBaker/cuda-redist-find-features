{
  buildPythonPackage,
  lib,
  # propagatedBuildInputs
  click,
  pydantic,
  typing-extensions,
  # passthru.optional-dependencies.dev
  black,
  mypy,
  pyright,
  ruff,
}: let
  toModuleName = builtins.replaceStrings ["-"] ["_"];
  moduleName = toModuleName attrs.pname;
  attrs = {
    pname = "cuda-redist-find-features";
    version = "0.1.0";
    format = "flit";
    src = lib.sources.sourceByRegex ../.. [
      "${moduleName}(:?/.*)?"
      "pyproject.toml"
    ];
    propagatedBuildInputs = [
      click
      pydantic
      typing-extensions
    ];
    pythonImportsCheck =
      builtins.map
      (drv: toModuleName drv.pname)
      (attrs.propagatedBuildInputs ++ [attrs]);
    passthru.optional-dependencies.dev = [
      black
      mypy
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
