# Yocto Tales

In this repository you will find some utilities to build linux images for some boards. The available images are:

1) Raspberry pi 3 image

2) Arty-Z7 100 image (WIP)

# Working with docker

The main idea is that we have a docker image with all the necessary tools.
We can create a local image and then enter to that shell using `scripts/dockershell.sh`.
Therefore, if we need to enter to that container in another terminal we can use: `docker exec -it <container_name> /bin/bash`. Be sure that you'll need to execute the entrypoint afterwards to have the environment ready: `source entrypoint.sh bash`.

# Quick start

Inside this repository you will find a CLI to build several linux images.
