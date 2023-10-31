# Taken from https://github.com/NixOS/nixpkgs/pull/244564
{
  annotated-types,
  buildPythonPackage,
  cloudpickle,
  dirty-equals,
  email-validator,
  faker,
  fetchFromGitHub,
  hatch-fancy-pypi-readme,
  hatchling,
  lib,
  pydantic-core,
  pytest-examples,
  pytest-mock,
  pytestCheckHook,
  typing-extensions,
}: let
  finalAttrs = {
    pname = "pydantic";
    version = "2.4.2";
    format = "pyproject";

    src = fetchFromGitHub {
      owner = finalAttrs.pname;
      repo = finalAttrs.pname;
      rev = "v${finalAttrs.version}";
      hash = "sha256-aW81VQRXFt4fxEyn3hV390ibvgrCCNqRRDPvbj8dMxU=";
    };

    patches = [
      ./01-remove-benchmark-flags.patch
    ];

    nativeBuildInputs = [
      hatch-fancy-pypi-readme
      hatchling
    ];

    propagatedBuildInputs = [
      annotated-types
      pydantic-core
      typing-extensions
    ];

    passthru.optional-dependencies = {
      email = [
        email-validator
      ];
    };

    pythonImportsCheck = ["pydantic"];

    nativeCheckInputs = [
      cloudpickle
      dirty-equals
      faker
      pytest-examples
      pytest-mock
      pytestCheckHook
    ];

    disabledTestPaths = [
      "tests/benchmarks"
    ];

    meta = with lib; {
      description = "Data validation using Python type hints";
      homepage = "https://github.com/pydantic/pydantic";
      changelog = "https://github.com/pydantic/pydantic/blob/v${version}/HISTORY.md";
      license = licenses.mit;
      maintainers = with maintainers; [connorbaker];
    };
  };
in
  buildPythonPackage finalAttrs
