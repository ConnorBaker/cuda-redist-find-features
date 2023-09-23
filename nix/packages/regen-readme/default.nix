{
  python3Packages,
  writeShellApplication,
}: let
  name = "regen-readme";
in
  writeShellApplication {
    inherit name;
    runtimeInputs = [python3Packages.cuda-redist-find-features];
    text = ''
      ${./. + "/${name}.sh"} ${./README_template.md}
    '';
  }
