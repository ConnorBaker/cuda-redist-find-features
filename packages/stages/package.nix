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
  text = ''
    for n in $(seq 0 4); do
      echo "Running stage $n";
      nix run --builders "" -L .#"stage''${n}";
      git add -A;
    done
  '';
}
