{writeShellApplication}: let
  name = "regen-readme";
in
  writeShellApplication {
    inherit name;
    runtimeInputs = [];
    text = ./. + "/${name}.sh";
  }
