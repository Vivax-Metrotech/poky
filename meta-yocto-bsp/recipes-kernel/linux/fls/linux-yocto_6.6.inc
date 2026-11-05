FILESEXTRAPATHS:prepend:beaglebone-yocto := "${THISDIR}/files:"

SRC_URI:append:beaglebone-yocto = " \
    file://iptables.cfg \
    file://flsfragments.cfg \
    file://0001-am335x-bone-common-add-fls-devices-and-clkout-overrides.patch \
    file://0002-am335x-bone-enable-legacy-fls-uarts-and-spi.patch \
    file://0003-am335x-boneblack-enable-legacy-fls-uarts-and-spi.patch \
    file://0005-am335x-boneblack-disable-hdmi-for-fls.patch \
"

KERNEL_CONFIG_FRAGMENTS:append:beaglebone-yocto = " \
    ${WORKDIR}/iptables.cfg \
    ${WORKDIR}/flsfragments.cfg \
"

SRCREV_machine:beaglebone-yocto = "f15178bbc6415aced18681b21246541beb52c894"
LINUX_VERSION:beaglebone-yocto = "6.6.144"
