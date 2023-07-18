{
  buildPythonApplication,
  lib,
  # propagatedBuildInputs
  pydantic,
  typing-extensions,
  # passthru.optional-dependencies.dev
  black,
  mypy,
  pyright,
  ruff,
}:
buildPythonApplication {
  pname = "cuda-redist-find-features";
  version = "0.1.0";
  format = "flit";
  src = lib.sources.sourceByRegex ../.. [
    "cuda_redist_find_features(:?/.*)?"
    "pyproject.toml"
  ];
  propagatedBuildInputs = [
    pydantic
    typing-extensions
  ];
  passthru.optional-dependencies.dev = [
    black
    mypy
    pyright
    ruff
  ];
  meta = with lib; {
    description = "Find features provided by a CUDA redistributable";
    homepage = "https://github.com/ConnorBaker/cuda-redist-find-features";
    maintainers = with maintainers; [connorbaker];
  };
}
