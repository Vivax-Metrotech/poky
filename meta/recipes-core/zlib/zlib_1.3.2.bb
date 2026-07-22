SUMMARY = "Zlib Compression Library"
DESCRIPTION = "Zlib is a general-purpose, patent-free, lossless data compression \
library which is used by many different programs."
HOMEPAGE = "https://zlib.net/"
SECTION = "libs"
LICENSE = "Zlib"
LIC_FILES_CHKSUM = "file://zlib.h;beginline=6;endline=23;md5=068c260be35209fb8458428c461dc536"

# The source tarball needs to be .gz as only the .gz ends up in fossils/
SRC_URI = "https://zlib.net/${BP}.tar.gz"
UPSTREAM_CHECK_URI = "https://zlib.net/"

SRC_URI[sha256sum] = "bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16"

# When a new release is made the previous release is moved to fossils/, so add this
# to PREMIRRORS so it is also searched automatically.
PREMIRRORS:append = " https://zlib.net/ https://zlib.net/fossils/"

CFLAGS += "-D_REENTRANT"

inherit ptest

B = "${WORKDIR}/build"

do_configure() {
	LDCONFIG=true ${S}/configure --prefix=${prefix} --shared --libdir=${libdir} --uname=GNU
}
do_configure[cleandirs] += "${B}"

do_compile() {
	oe_runmake shared
}

do_install() {
	oe_runmake DESTDIR=${D} install
}

BBCLASSEXTEND = "native nativesdk"

# Adding 'CVE_PRODUCT' to avoid false detection of CVEs
CVE_PRODUCT = "zlib:zlib gnu:zlib"

CVE_STATUS[CVE-2026-22184] = "not-applicable-config: vulnerable file is not compiled"
