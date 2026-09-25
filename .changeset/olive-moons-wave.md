---
"@platforma-open/milaboratories.cell-ranger": patch
---

Pin `@platforma-sdk/block-tools` to 2.16.1 and `@platforma-sdk/tengo-builder` to 4.1.1,
the two packages the `require-latest` CI preflight checks.

Bump `@platforma-sdk/package-builder` to 3.16.0. 3.12.0 refused to build docker images
on an arm64 host, although `docker.build` already pins `--platform linux/amd64` to
cross-compile. Without an image the k8s runner fails with "docker image is not
specified", so no software change in this block could be tested against a remote
backend from a Mac.
