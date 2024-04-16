{
  writers,
  python312,
  python312Packages,
  buildPackages,
}:
writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
  "/bin/generate_index"
  {
    flakeIgnore = [
      "E501" # line too long
      "W503" # line break before binary operator
    ];
  }
  (builtins.readFile ./generate_index.py)
