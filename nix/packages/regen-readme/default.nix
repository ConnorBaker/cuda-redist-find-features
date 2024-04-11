{ cuda-redist-find-features, writeShellApplication }:
let
  name = "regen-readme";
in
writeShellApplication {
  inherit name;
  runtimeInputs = [ cuda-redist-find-features ];
  text = ''
    ${./. + "/${name}.sh"} ${./README_template.md}
  '';
}
