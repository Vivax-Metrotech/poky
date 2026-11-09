FLS BeagleBone Black kernel customizations
=========================================

The Linux 6.18 append in the parent directory applies the patches and
configuration files here for MACHINE=beaglebone-yocto. Other machines
retain their existing kernel configuration. The 6.6 include preserves
the earlier release configuration; the current FLS image uses 6.18.

The patches modify GPL-2.0-only Linux kernel and device-tree sources.
Preserve the upstream copyright and license notices when distributing
the modified source. The kernel recipe identifies the exact Linux and
kernel-cache revisions needed alongside these patches and build files.

Patch inventory:
0001: FLS devices and clock-output configuration
0002: legacy UART/SPI configuration in am335x-bone.dts
0003: BeagleBone Black UART/SPI configuration
0004: stable legacy GPIO numbering
0005: disable unused HDMI
0006: clock aliases for long AM335x device names
0007: early timer provider dependencies
0008: skip the unused AM335x legacy voltage initialization layer

No proprietary application source or signing keys are needed to build
the kernel. Enable meta and meta-yocto-bsp, select beaglebone-yocto and
linux-yocto 6.18, and run bitbake virtual/kernel. Preserve the effective
kernel .config with each distributed binary release.

Watchdog sysfs diagnostics are enabled so state, timeout and time remaining
can be read without opening or feeding /dev/watchdog. This does not change
the existing owner, 60-second driver default or CONFIG_WATCHDOG_NOWAYOUT=n.
Do not write sysfs policy attributes during fault observation. A bootstatus
value of zero does not prove that a preceding watchdog reset did not occur:
the OMAP driver's reset-source callback is platform-data dependent.
