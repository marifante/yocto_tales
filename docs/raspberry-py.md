# Creating an image for Raspbperry Pi


Luckily, there is already a meta layer for raspberry pi: https://git.yoctoproject.org/meta-raspberrypi/tree/README.md?h=dunfell.

This layer depends on other 2 layers:
* URI: git://git.yoctoproject.org/poky
  * branch: master
  * revision: HEAD

* URI: git://git.openembedded.org/meta-openembedded
  * layers: meta-oe, meta-multimedia, meta-networking, meta-python
  * branch: master
  * revision: HEAD

This was done following this article: https://medium.com/nerd-for-tech/build-your-own-linux-image-for-the-raspberry-pi-f61adb799652.  
