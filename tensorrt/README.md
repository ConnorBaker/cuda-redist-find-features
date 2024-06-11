# tensorrt

These redistributable manifests are made by hand to allow TensorRT to be packaged with the same functionality the other NVIDIA redistributable libraries are packaged with.

Only available from 10.0.0 and onwards, which is when NVIDIA stopped putting them behind a login wall.

You can find them at: <https://github.com/NVIDIA/TensorRT?tab=readme-ov-file#optional---if-not-using-tensorrt-container-specify-the-tensorrt-ga-release-build-path>.

After using `nix store prefetch-file` to get the store path of the tarball, you need to convert it to a base16 SHA256 and MD5 hash, and then get the size of the file in bytes.

As an example:

```console
nix store prefetch-file --json https://developer.nvidia.com/downloads/compute/machine-learning/tensorrt/10.0.1/tars/TensorRT-10.0.1.6.Linux.x86_64-gnu.cuda-11.8.tar.gz
nix hash file --type md5 --base16 /nix/store/7szksc9lwfpq6xqyyw6mrlk0fp4f6nmg-TensorRT-10.0.1.6.Linux.x86_64-gnu.cuda-11.8.tar.gz
nix hash file --type sha256 --base16 /nix/store/7szksc9lwfpq6xqyyw6mrlk0fp4f6nmg-TensorRT-10.0.1.6.Linux.x86_64-gnu.cuda-11.8.tar.gz
du -b /nix/store/7szksc9lwfpq6xqyyw6mrlk0fp4f6nmg-TensorRT-10.0.1.6.Linux.x86_64-gnu.cuda-11.8.tar.gz
```
