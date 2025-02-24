# Creating a BSP

A BSP (Board Support Package) should contain all the features for the **board** that we will be using.
For example, if we'll use the Arty Z7 devkit, we should have a BSP for that board.
It contains:
* The device-tree
* The kernel configuration
* The U-Boot configuration


To create a BSP we should do the following:

1) Create a docker container with the required setup. You can use the script `scripts/dockershell.sh`.
2) Setup yocto:

```bash
repo init -u https://github.com/Xilinx/yocto-manifests.git -b rel-v2023.2
repo sync
source setupsdk
```

3) Build the linux image with yocto. Select the correct image with MACHINE env var and pick the correct recipe.

```bash
export RECIPE="petalinux-image-minimal"
MACHINE=zynq-generic bitbake ${RECIPE}
```

This process can take some time. If it is the first time you run it you will not have anything cached, which will lead into a big ETA.

During the process, the following output files will be created in work directory (specifically in ${WORK_DIRECTORY}/build/tmp/deploy/images/zynq-generic) and should be copied to `boot` partition on the SD:
* boot.scr
* boot.bin
* zynq-generic-system.dtb
* uImage (for 32 bit processors) and Image (for 64 bits processors)

The only needed binary to boot up from SD is `boot.bin`. So you need to copy it to the boot partition of the SD (often as `BOOT.bin`).
There is a convenience script in `scripts/burn_to_sd.sh` that takes care of this part of the process. That script will format the SD and copy all the necessary files.

Also the rootfs will be there, you can extract it in rootfs partition of the SD as well:

* tar xf petalinux-image-minimal-zynq-generic.tar.gz -c -C `${SD}/rootfs`


# Tweaking device tree

You can always reverse the `.dtb` to see what is the actual `.dts` behind it:
```
dtc -I dtb -O dts -o system.dts zynq-generic-system.dtb
```

# Creating a new Yocto layer for a new machine

1) In work directory use `bitbake-layers create-layer` to generate base layer.

```bash
embeddev@040a45f4faa6:~/yocto_tales/work$ export LAYER=/home/embeddev/yocto_tales/layers/meta-artyz7
embeddev@040a45f4faa6:~/yocto_tales/work$ ^C
embeddev@040a45f4faa6:~/yocto_tales/work$ bitbake-layers create-layer $LAYER
NOTE: Starting bitbake server...
NOTE: Started PRServer with DBfile: /home/embeddev/yocto_tales/work/build/cache/prserv.sqlite3, Address: 127.0.0.1:37245, PID: 88
Add your new layer with 'bitbake-layers add-layer /home/embeddev/yocto_tales/layers/meta-artyz7'
```

At this point you will have a "template" layer with some things already created, like the `conf/layer.conf` file and a example recipe.

2) Add the layer to `bblayers.conf` file to allow bitbake buildsystem to find the new layer.
This file will be located in `work/build/conf/bblayers.conf`. We have a yocto script called `bitbake-layers add-layer` to add a layer into that file (so we can avoid typos). That script should be executed from the build directory (`work/build`), because if not bitbake will not find bblayers.conf.

```bash
embeddev@040a45f4faa6:~/yocto_tales/work/build/conf$ cd ..
embeddev@040a45f4faa6:~/yocto_tales/work/build$ bitbake-layers add-layer $LAYER
NOTE: Starting bitbake server...
NOTE: Started PRServer with DBfile: /home/embeddev/yocto_tales/work/build/cache/prserv.sqlite3, Address: 127.0.0.1:43697, PID: 251
```

3) Now if you execute `bitbake-layers show-layers` you should find the new layer in the output.

4) Now you can add all the things you like to the new layer.

5) Then you can build again `MACHINE=artyz7-zynq7 bitbake petalinux-image-minimal`.


# Troubleshooting

## My Linux doesn't boot. What can go wrong?

1) First of all, try to download a prebuilt image from Xilin and burn it to a SD. Then try to bootup the device with that image. If the device doesn't boot with that image, something may be wrong with the hardware.

You can find a list of prebuilt images here: https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/3105161217/2024.2+Release#Downloads.
Usually, those images come in a `.wic` format. You will need to flash it to the SD with dd: `dd if=petalinux-sdimage.wic of=/dev/sd<X> conv=fsync`.

# References

* https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/18841862/Install+and+Build+with+Xilinx+yocto
* https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/2823422188/Building+Yocto+Images+using+a+Docker+Container
* https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/57836605/Creating+a+Custom+Yocto+Layer
