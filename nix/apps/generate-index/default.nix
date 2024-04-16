{
  writers,
  python312,
  python312Packages,
  buildPackages,
}:
writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
  "/bin/generate_index"
  { flakeIgnore = [ "E501" ]; }
  (builtins.readFile ./generate_index.py)
