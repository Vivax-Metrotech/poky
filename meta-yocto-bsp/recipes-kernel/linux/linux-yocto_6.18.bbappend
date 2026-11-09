FILESEXTRAPATHS:prepend:beaglebone-yocto := "${THISDIR}/fls/files:"
PR:beaglebone-yocto = "r2"

COMPATIBLE_MACHINE:beaglebone-yocto = "beaglebone-yocto"
KBRANCH:beaglebone-yocto = "v6.18/standard/beaglebone"
KMACHINE:beaglebone-yocto ?= "beaglebone"

SRC_URI:append:beaglebone-yocto = " \
    file://iptables.cfg \
    file://flsfragments.cfg \
    file://0001-am335x-bone-common-add-fls-devices-and-clkout-overrides.patch \
    file://0002-am335x-bone-enable-legacy-fls-uarts-and-spi.patch \
    file://0003-am335x-boneblack-enable-legacy-fls-uarts-and-spi.patch \
    file://0004-am335x-boneblack-preserve-fls-gpio-numbers.patch \
    file://0005-am335x-boneblack-disable-hdmi-for-fls.patch \
    file://0006-clkdev-allow-am335x-device-names.patch \
    file://0007-am335x-system-timer-post-init-providers.patch \
    file://0008-am335x-skip-unused-omap-voltage-layer.patch \
    file://fls-production.scc \
"

KERNEL_CONFIG_FRAGMENTS:append:beaglebone-yocto = " \
    ${WORKDIR}/iptables.cfg \
    ${WORKDIR}/flsfragments.cfg \
"

KERNEL_FEATURES:remove:beaglebone-yocto = "features/debug/debug-kernel.scc features/scsi/scsi-debug.scc features/nf_tables/nft_test.scc features/gpio/mockup.scc features/gpio/sim.scc"
KERNEL_FEATURES:append:beaglebone-yocto = " features/gpio/sysfs.scc features/nf_tables/nf_tables.scc fls-production.scc"

SRCREV_machine:beaglebone-yocto = "a05c451ede0dd80b1cc2362b47f36f3c137cbd1e"
LINUX_VERSION:beaglebone-yocto = "6.18.39"

# symbol_why.py/kconfiglib in this scarthgap tree cannot parse newer 6.18
# Kconfig syntax like "transitional", so skip the audit-only config check.
do_kernel_configcheck[noexec] = "${@'1' if d.getVar('MACHINE') == 'beaglebone-yocto' else ''}"
