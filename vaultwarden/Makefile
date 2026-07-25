DESTDIR ?=
BINDIR ?= /usr/bin
SYSCONFDIR ?= /etc
UNITDIR ?= /usr/lib/systemd/system
STATEDIR ?= /var/lib/vaultwarden
LOGDIR ?= /var/log/vaultwarden

RPM_OUTPUT_DIR ?= $(CURDIR)/out
# Empty by default: inside the AlmaLinux build container %dist already
# expands to .el9 / .el10 on its own.
DIST ?=

build:
	# [ -f output/vaultwarden ] || ./docker-image-extract vaultwarden/server:1.25.0-alpine
	# ./build-in-docker.sh
	echo OK

install:
	install -d -m 755 $(DESTDIR)$(BINDIR)
	install -d -m 755 $(DESTDIR)$(SYSCONFDIR)
	install -d -m 755 $(DESTDIR)$(SYSCONFDIR)/logrotate.d
	install -d -m 755 $(DESTDIR)$(UNITDIR)
	install -d -m 750 $(DESTDIR)$(STATEDIR)
	install -d -m 750 $(DESTDIR)$(STATEDIR)/data
	install -d -m 750 $(DESTDIR)$(LOGDIR)
	install -m 755 target/release/vaultwarden $(DESTDIR)$(BINDIR)/vaultwarden
	install -m 640 vaultwarden.env $(DESTDIR)$(SYSCONFDIR)/vaultwarden.env
	install -m 644 rpm/vaultwarden.service $(DESTDIR)$(UNITDIR)/vaultwarden.service
	install -m 644 rpm/vaultwarden.logrotate $(DESTDIR)$(SYSCONFDIR)/logrotate.d/vaultwarden

# --build-in-place keeps %{_builddir} pointed at this checkout, so the binary
# cargo just produced in target/release is what gets packaged.
rpm:
	rpmbuild -bb --build-in-place \
	    --define "_rpmdir $(RPM_OUTPUT_DIR)" \
	    $(if $(DIST),--define "dist $(DIST)") \
	    rpm/vaultwarden.spec

.PHONY: build install rpm
