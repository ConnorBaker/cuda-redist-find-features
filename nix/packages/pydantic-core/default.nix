{
  stdenv,
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  cargo,
  rustPlatform,
  rustc,
  libiconv,
  typing-extensions,
  pytestCheckHook,
  hypothesis,
  pytest-timeout,
  pytest-mock,
  dirty-equals,
}:
buildPythonPackage rec {
  pname = "pydantic-core";
  version = "2.10.1";
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "pydantic";
    repo = "pydantic-core";
    rev = "a8fb1e3f46598498b2f01d2a5949ae501739717f";
    hash = "sha256-WBcvFVsJvK/euOpbDTQDtftoFushkjDzu4DjHYAD6YU=";
    # We need something slightly newer than the latest release because it fixes issues with generics.
    # rev = "v${version}";
    # hash = "sha256-D7FOnSYMkle+Kl+ORDXpAGtSYyDzR8FnkZxjEY1BIqs=";
  };

  patches = [
    ./01-remove-benchmark-flags.patch
  ];

  cargoDeps = rustPlatform.fetchCargoTarball {
    inherit src;
    hash = "sha256-X2s/VwM5emCq2bcEqcezoC9wnoP6UU0CgeM0x2PlzgI=";
  };

  nativeBuildInputs = [
    cargo
    rustPlatform.cargoSetupHook
    rustPlatform.maturinBuildHook
    rustc
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
    pytestCheckHook
    hypothesis
    pytest-timeout
    dirty-equals
    pytest-mock
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
    maintainers = with maintainers; [blaggacao];
  };
}
