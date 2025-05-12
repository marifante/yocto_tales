# Yocto Tales

In this repository you will find some utilities to build linux images for some boards. The available images are:

1. Raspberry pi 3 image

2. Arty-Z7 100 image (WIP)

# Working with docker

The main idea is that we have a docker image with all the necessary tools.
We can create a local image and then enter to that shell using `scripts/dockershell.sh`.
Therefore, if we need to enter to that container in another terminal we can use: `docker exec -it <container_name> /bin/bash`. Be sure that you'll need to execute the entrypoint afterwards to have the environment ready: `source entrypoint.sh bash`.

# Quick start

Inside this repository you will find a CLI to build several linux images.

# Usage

1. Create a configuration file. You can use the `config/raspberry_pi_3_minimal/config.yml` as a template. The configuration file is a YAML file that contains the following fields:

```YAML
name: the name of the image
layers:
    - uri: uri of the repository that will be cloned to use meta-layer 0
      revision: tag, sha or branch of the repository that will be used

    - uri: uri of the repository that will be cloned to use meta-layer 1
      revision: tag, sha or branch of the repository that will be used

    - uri: uri of the repository that will be cloned to use meta-layer N
      revision: tag, sha or branch of the repository that will be used

bitbake:
    image: name of the image that will be built
    setup:
        - call: command 1 that will be executed before issuing bitbake command.
        - call: command 2 that will be executed before issuing bitbake command.
        - call: command N that will be executed before issuing bitbake command.
```

2. Create `local.conf` and `bblayers.conf` files _in the same directory_ as the main `.yml` config file. You can use the `config/raspberry_pi_3_minimal/local.conf` and `config/raspberry_pi_3_minimal/bblayers.conf` as a template. The `local.conf` file is used to configure the build system, while the `bblayers.conf` file is used to configure the layers that will be used during the build.

## Build files

In yocto, there are some files used during build to configure some aspects of the image. Usually those files are located inside `build/conf` folder.
The most important files are:

1. `local.conf`: This file is used to configure the build system. It contains settings such as the target machine, the number of parallel threads to use during the build, and other build options.
2. `bblayers.conf`: This file is used to configure the layers that will be used during the build. It contains a list of layers and their paths, as well as other layer-specific settings.

Yoctales takes care of this in the following way. All of this happens before `bitbake` build command is executed.

1. It will search inside the directory in which the config file is located if any `local.conf` and/or `bblayers.conf` file are present.
2. If no file is present, it will throw an error and just exit.
3. If all those files are present, then it will copy them to `build/conf` folder.
