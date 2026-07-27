DESTDIR ?=
DATADIR ?= /usr/share

RPM_OUTPUT_DIR ?= $(CURDIR)/out
# Set explicitly when building this noarch package outside of an EL host,
# where %dist would otherwise expand to nothing.
DIST ?=

build:
	[ -f bw_web_${VW_WEB_VERSION}.tar.gz ] || wget -O bw_web_${VW_WEB_VERSION}.tar.gz https://github.com/dani-garcia/bw_web_builds/releases/download/${VW_WEB_VERSION}/bw_web_${VW_WEB_VERSION}.tar.gz

install:
	install -d -m 755 $(DESTDIR)$(DATADIR)/vaultwarden
	tar -f bw_web_$(VW_WEB_VERSION).tar.gz -C $(DESTDIR)$(DATADIR)/vaultwarden -xz

# --nodeps: this noarch package is built on the CI host, whose rpm database is
# empty, so BuildRequires could never be satisfied there. They stay in the spec
# to document what a rebuild on an EL host needs; the payload is just an
# unpacked tarball, so nothing links against anything.
rpm: build
	rpmbuild -bb --build-in-place --nodeps \
	    --define "_rpmdir $(RPM_OUTPUT_DIR)" \
	    $(if $(DIST),--define "dist $(DIST)") \
	    rpm/vaultwarden-web-vault.spec

.PHONY: build install rpm
