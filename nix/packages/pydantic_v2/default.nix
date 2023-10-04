# Taken from https://github.com/NixOS/nixpkgs/pull/244564
{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  hatch-fancy-pypi-readme,
  hatchling,
  annotated-types,
  pydantic-core,
  typing-extensions,
  email-validator,
  pytestCheckHook,
  dirty-equals,
  pytest-examples,
  pytest-mock,
  faker,
}:
buildPythonPackage rec {
  pname = "pydantic";
  version = "2.4.2";
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "pydantic";
    repo = "pydantic";
    rev = "0c444b3da46fcfd8a5b9a949a5335aa067faa2c0";
    hash = "sha256-TrPgAj8AbI5rVVrMtilm43isz8fhPfPisqM1NaL0tns=";
    # We need something slightly newer than the latest release because it fixes issues with generics.
    # rev = "v${version}";
    # hash = "sha256-aW81VQRXFt4fxEyn3hV390ibvgrCCNqRRDPvbj8dMxU=";
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
    pytestCheckHook
    dirty-equals
    pytest-mock
    pytest-examples
    faker
  ];

  disabledTestPaths = [
    "tests/benchmarks"
  ];

  meta = with lib; {
    description = "Data validation using Python type hints";
    homepage = "https://github.com/pydantic/pydantic";
    changelog = "https://github.com/pydantic/pydantic/blob/v${version}/HISTORY.md";
    license = licenses.mit;
    maintainers = with maintainers; [wd15];
  };
}
