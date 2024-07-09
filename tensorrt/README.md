# tensorrt

These redistributable manifests are made by hand to allow TensorRT to be packaged with the same functionality the other NVIDIA redistributable libraries are packaged with.

Only available from 10.0.0 and onwards, which is when NVIDIA stopped putting them behind a login wall.

You can find them at: <https://github.com/NVIDIA/TensorRT?tab=readme-ov-file#optional---if-not-using-tensorrt-container-specify-the-tensorrt-ga-release-build-path>.

Construct entries using the provider `helper.sh` script.

As an example:

```console
$ ./tensorrt/helper.sh 11.8 10.0.1.6 linux-x86_64
main: storePath: /nix/store/3wah1b4z19pnlxi85mi30whx7jcrin1s-TensorRT-10.0.1.6.l4t.aarch64-gnu.cuda-12.4.tar.gz
{
  "linux-aarch64": {
    "cuda12": {
      "md5": "34a63595d03ef613a8c5e152f32cb3a7",
      "relative_path": "tensorrt/10.0.1/tars/TensorRT-10.0.1.6.l4t.aarch64-gnu.cuda-12.4.tar.gz",
      "sha256": "cb56e30a7f6819f6f1af8c2cd417e71e47c97b52d978ad06f3365858aafccbbf",
      "size": "666711593"
    }
  }
}
```

The `storePath` is useful for determining the date of the release.
