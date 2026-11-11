FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://0001-signature-send-OpenSSL-diagnostics-to-stderr.patch"
PR:append = ".stdio1"
