{ nixVersions, writeShellApplication }:
writeShellApplication {
  name = "stages";
  runtimeInputs = [ nixVersions.unstable ];
  derivationArgs = {
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  text =
    # Loop over the stages and run them
    ''
      for idx in mk-index-of-sha256-and-relative-path mk-index-of-package-info; do
        echo "Running: $idx"
        nix run --builders "" -L ".#$idx"
        echo "Adding all changes to git"
        git add --all
      done
    '';
}
