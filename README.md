# Yocto Tales

In this repository you will find some utilities to build linux images with docker.

## Working with docker

The main idea is that we have a docker image with all the necessary tools.
We can create a local image and then enter to that shell using `scripts/dockershell.sh`.
Therefore, if we need to enter to that container in another terminal we can use: `docker exec -it <container_name> /bin/bash`. Be sure that you'll need to execute the entrypoint afterwards to have the environment ready: `source entrypoint.sh bash`.

Docker images are being built in CI using GitHub Actions. After ever PR is merged into main, a new image is tagged as latest.

## Running QEMU in docker

If you are running QEMU in a docker container, you need to make sure that:

- you are mounting device `/dev/net/tun` in the container through docker run command (`--device=/dev/net/tun`).
- you are giving NET_ADMIN capability to the container using `--cap-add=NET_ADMIN` option in the docker run command. This is already being done in the `scripts/dockershell.sh` script.
- it is easier if you pass the flag `nographic` to QEMU, so you can see the output in your dockershell. By default `runqemu` script inside OE build environment will try to open a graphical window. For example, you could use: `runqemu qemuarm nographic`.
