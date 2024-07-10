{
  buildPackages,
  cuda-redist-lib,
  python312,
  python312Packages,
  writers,
}:
writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
  "/bin/mk-index-of-sha256-and-relative-path"
  {
    flakeIgnore = [
      "E501" # line too long
      "W503" # line break before binary operator
    ];
    libraries = [ cuda-redist-lib ];
  }
  (builtins.readFile ./mk_index_of_sha256_and_relative_path.py)
