# tensorrt

These redistributable manifests are made by hand to allow TensorRT to be packaged with the same functionality the other NVIDIA redistributable libraries are packaged with.

After using `nix store prefetch-file` to get the hash of the tarball, you need to convert it to a base64 hash:

```console
nix hash convert --from sri --to base64 <hash>
```
