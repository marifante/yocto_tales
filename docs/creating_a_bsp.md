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

3) Build the linux image with yocto. Select the correct image with MACHINE env var:

```bash
MACHINE=zynq-generic bitbake petalinux-image-minimal
```

This process can take some time. If it is the first time you run it you will not have anything cached, which will lead into a big ETA.

During the process, the following output files will be created in work directory (specifically in ${WORK_DIRECTORY}/build/tmp/deploy/images/zynq-generic) and should be copied to `boot` partition on the SD:
* boot.scr -> `${SD}/boot/boot.scr`
* boot.bin -> `${SD}/boot/boot.bin`
* zynq-generic-system.dtb -> `${SD}/boot/system.dtb`
* If your processor is 32 bits: uImage -> `${SD}/boot/uImage`
* If your processor is 64 bits: Image -> `${SD}/boot/Image`

Also the rootfs will be there, you can extract it in rootfs partition of the SD as well:

* tar xf petalinux-image-minimal-zynq-generic.tar.gz -c -C `${SD}/rootfs`

There is a convenience script in `scripts/burn_to_sd.sh` that takes care of this part of the process. That script will format the SD and copy all the necessary files.

# References

* https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/18841862/Install+and+Build+with+Xilinx+yocto
* https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/2823422188/Building+Yocto+Images+using+a+Docker+Container
