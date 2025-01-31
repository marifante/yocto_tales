# Linux Booting Process on Zynq Platform


1) Boot ROM: reads the value of the boot strapping pins to determine the boot mode (JTAG, NAND flash, QSPI Flash, SD Card, etc). Then it will load the First Stage BootLoader (FSBL) image from the interface specified by the boot mode.

2) First Stage Bootloader: The FSBL execute some instructions to initialise the PS with and to configure the PL with a given bitstream.
The FSBL is included inside the `boot.bin` file.

3) Second Stage Bootloader: This is U-boot.

# References

* https://kleinembedded.com/understanding-the-embedded-linux-boot-process/
* https://www.fpgakey.com/tutorial/section520#:~:text=As%20previously%20explained%20in%20this,the%20optional%20bitstream%20and%20SSBL.
