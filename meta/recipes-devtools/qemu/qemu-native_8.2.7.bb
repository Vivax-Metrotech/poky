BPN = "qemu"

DEPENDS += "glib-2.0-native zlib-native"

require qemu-native.inc

EXTRA_OECONF:append = " --target-list=${@get_qemu_usermode_target_list(d)} --disable-tools --disable-install-blobs --disable-guest-agent"

# Linux user-mode tests must preserve xattrs instead of returning ENOSYS when
# guest applications atomically replace existing configuration files.
PACKAGECONFIG ??= "pie ${@bb.utils.contains('BUILD_OS', 'linux', 'attr', '', d)}"
