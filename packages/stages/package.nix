{ nixVersions, writeShellApplication }:
writeShellApplication {
  name = "stages";
  runtimeInputs = [ nixVersions.unstable ];
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  # Avoid using `cp` here because it'll error if the file already exists and have troubles with perms.
  text =
    # Set defaults
    ''
      declare -i start=0
      declare -i stop=4
    ''
    # Switch on arguments passed to the script
    + ''
      while (( "$#" )); do
        case "$1" in
          --start)
            start=$2
            shift 2
            ;;
          --stop)
            stop=$2
            shift 2
            ;;
          *)
            echo "Usage: $(basename "$0") [--start <start>] [--stop <stop>]"
            echo "  --start: The stage to start at (default: 0)"
            echo "  --stop: The stage to stop at (default: 4)"
            exit 1
            ;;
        esac
      done
    ''
    # Loop over the stages and run them
    + ''
      for n in $(seq $start $stop); do
        echo "Running stage $n"
        nix run --builders "" -L .#"stage''${n}"
        echo "Adding all changes to git"
        git add --all
      done
    '';
}
