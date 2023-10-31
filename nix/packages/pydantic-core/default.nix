{
  buildPythonPackage,
  cargo,
  dirty-equals,
  fetchFromGitHub,
  hypothesis,
  lib,
  libiconv,
  pytest-mock,
  pytest-timeout,
  pytestCheckHook,
  rustc,
  rustPlatform,
  stdenv,
  typing-extensions,
}: let
  finalAttrs = {
    pname = "pydantic-core";
    version = "2.11.0";
    format = "pyproject";

    src = fetchFromGitHub {
      owner = "pydantic";
      repo = finalAttrs.pname;
      rev = "v${finalAttrs.version}";
      hash = "sha256-jEPIUYybpTaKv3uTuG3OHgWKBQ0CtTez1XWVwmCmM1E=";
    };

    patches = [
      ./01-remove-benchmark-flags.patch
    ];

    cargoDeps = rustPlatform.fetchCargoTarball {
      inherit (finalAttrs) src;
      hash = "sha256-kmJafvh9WN8XNfLwsKq6kA/KRj4Snzc9G9R4eZUHP38=";
    };

    nativeBuildInputs = [
      cargo
      rustc
      rustPlatform.cargoSetupHook
      rustPlatform.maturinBuildHook
      typing-extensions
    ];

    buildInputs = lib.optionals stdenv.isDarwin [
      libiconv
    ];

    propagatedBuildInputs = [
      typing-extensions
    ];

    pythonImportsCheck = ["pydantic_core"];

    nativeCheckInputs = [
      dirty-equals
      hypothesis
      pytest-mock
      pytest-timeout
      pytestCheckHook
    ];

    disabledTests = [
      # RecursionError: maximum recursion depth exceeded while calling a Python object
      "test_recursive"
    ];

    disabledTestPaths = [
      # no point in benchmarking in nixpkgs build farm
      "tests/benchmarks"
    ];

    meta = with lib; {
      description = "Core validation logic for pydantic written in rust";
      homepage = "https://github.com/pydantic/pydantic-core";
      license = licenses.mit;
      maintainers = with maintainers; [connorbaker];
    };
  };
in
  buildPythonPackage finalAttrs
