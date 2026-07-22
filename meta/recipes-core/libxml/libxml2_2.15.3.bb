SUMMARY = "XML C Parser Library and Toolkit"
DESCRIPTION = "The XML Parser Library allows for manipulation of XML files. Libxml2 exports Push and Pull type parser interfaces for both XML and HTML. It can do DTD validation at parse time, on a parsed document instance or with an arbitrary DTD. Libxml2 includes complete XPath, XPointer and Xinclude implementations."
HOMEPAGE = "https://gitlab.gnome.org/GNOME/libxml2"
BUGTRACKER = "http://bugzilla.gnome.org/buglist.cgi?product=libxml2"
SECTION = "libs"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://Copyright;md5=5873615e8a9ecbf5c8857c4312ee05d6 \
                    file://dict.c;beginline=6;endline=15;md5=2b4b7b827d2d8b080372433c4c9c85b6 \
                    file://list.c;beginline=4;endline=13;md5=b9c25b021ccaf287e50060602d20f3a7 \
                    "

DEPENDS = "zlib virtual/libiconv"

GNOMEBASEBUILDCLASS = "autotools"
inherit gnomebase

SRC_URI[archive.sha256sum] = "78262a6e7ac170d6528ebfe2efccdf220191a5af6a6cd61ea4a9a9a5042c7a07"

# Disputed as a security issue, but fixed in d39f780
CVE_STATUS[CVE-2023-45322] = "disputed: issue requires memory allocation to fail"

BINCONFIG = "${bindir}/xml2-config"

PACKAGECONFIG ??= "python"
PACKAGECONFIG[python] = "--with-python=${PYTHON},--without-python,python3"

inherit autotools pkgconfig binconfig-disabled

inherit_defer ${@bb.utils.contains('PACKAGECONFIG', 'python', 'python3targetconfig', '', d)}

# WARNING: zlib is required for RPM use
EXTRA_OECONF = "--without-debug --without-legacy --with-catalog --with-c14n"
EXTRA_OECONF:class-native = "--without-legacy --with-c14n --with-zlib"
EXTRA_OECONF:class-nativesdk = "--without-legacy --with-c14n --with-zlib"
EXTRA_OECONF:linuxstdbase = "--with-debug --with-legacy --with-c14n --with-zlib"

python populate_packages:prepend () {
    # autonamer would call this libxml2-2, but we don't want that
    if d.getVar('DEBIAN_NAMES'):
        d.setVar('PKG:libxml2', '${MLPREFIX}libxml2')
}

PACKAGE_BEFORE_PN += "${PN}-utils"
PACKAGES += "${PN}-python"

FILES:${PN}-staticdev += "${PYTHON_SITEPACKAGES_DIR}/*.a"
FILES:${PN}-utils = "${bindir}/*"
FILES:${PN}-python = "${PYTHON_SITEPACKAGES_DIR}"

do_install:append:class-native () {
	# Docs are not needed in the native case
	rm ${D}${datadir}/gtk-doc -rf

	create_wrapper ${D}${bindir}/xmllint 'XML_CATALOG_FILES=${XML_CATALOG_FILES:-${sysconfdir}/xml/catalog}'
}
do_install[vardepsexclude] += "XML_CATALOG_FILES:-${sysconfdir}/xml/catalog"

BBCLASSEXTEND = "native nativesdk"
