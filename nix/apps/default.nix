{
  perSystem =
    { config, pkgs, ... }:
    {
      apps = {
        generate-index.program =
          let
            generate-index = pkgs.callPackage ./generate-index { inherit (config.packages) cuda-redist-lib; };
          in
          "${generate-index}/bin/${generate-index.meta.mainProgram}";
        generate-hash-to-nar-hash.program =
          let
            generate-hash-to-nar-hash = pkgs.callPackage ./generate-hash-to-nar-hash { };
          in
          "${generate-hash-to-nar-hash}/bin/${generate-hash-to-nar-hash.meta.mainProgram}";
      };
    };
}
