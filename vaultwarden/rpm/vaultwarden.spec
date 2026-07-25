# RPM counterpart of the former debian/ directory.
#
# The binary is compiled by cargo before rpmbuild runs (see ../Dockerfile),
# so this spec only packages the result and compiles nothing itself.
# rpmbuild is invoked with --build-in-place, which points the build directory
# at the checkout, the same way dpkg-buildpackage worked in the deb variant.
#
# Note: keep section names out of comments, rpm parses them as section
# markers even behind a hash.

# Minimum web vault version this server release expects.
# Kept in sync by ../../generate-files.py.
%global vw_web_version 2026.6.4

# The Rust binary carries no useful DWARF for a separate debuginfo package,
# and find-debuginfo would fail on the missing sources.
%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0

Name:           vaultwarden
Version:        1.37.0
Release:        1%{?dist}
Summary:        Unofficial Bitwarden compatible server written in Rust

License:        AGPL-3.0-only
URL:            https://github.com/dani-garcia/vaultwarden
# Sources are unpacked into the build directory by the Dockerfile, not by rpm.
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  make
BuildRequires:  systemd-rpm-macros

Requires:       vaultwarden-web-vault >= %{vw_web_version}
Requires(pre):  shadow-utils
# libmariadb.so.3 / libpq.so.5 are picked up automatically from the ELF
# dependencies of the binary, so they are not listed explicitly here.

%description
Alternative implementation of the Bitwarden server API written in
Rust and compatible with upstream Bitwarden clients, perfect for
self-hosted deployment where running the official resource-heavy
service might not be ideal.

%build
# Nothing to do: the binary is already at target/release/vaultwarden.

%install
%make_install \
    BINDIR=%{_bindir} \
    SYSCONFDIR=%{_sysconfdir} \
    UNITDIR=%{_unitdir} \
    STATEDIR=%{_sharedstatedir}/vaultwarden \
    LOGDIR=%{_localstatedir}/log/vaultwarden

%pre
getent group vaultwarden >/dev/null || groupadd -r vaultwarden
getent passwd vaultwarden >/dev/null || \
    useradd -r -g vaultwarden -d %{_sharedstatedir}/vaultwarden -s /sbin/nologin \
            -c "vaultwarden system user" vaultwarden
exit 0

%post
%systemd_post vaultwarden.service

%preun
%systemd_preun vaultwarden.service

%postun
%systemd_postun_with_restart vaultwarden.service

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/vaultwarden
%{_unitdir}/vaultwarden.service
# The env file holds ADMIN_TOKEN and SMTP credentials: readable by the
# service account only, unlike the world-readable deb variant.
%config(noreplace) %attr(0640,root,vaultwarden) %{_sysconfdir}/vaultwarden.env
%config(noreplace) %{_sysconfdir}/logrotate.d/vaultwarden
%dir %attr(0750,vaultwarden,vaultwarden) %{_sharedstatedir}/vaultwarden
%dir %attr(0750,vaultwarden,vaultwarden) %{_sharedstatedir}/vaultwarden/data
%dir %attr(0750,vaultwarden,vaultwarden) %{_localstatedir}/log/vaultwarden

%changelog
* Sat Jul 25 2026 Laurier Sylph. <laurier@sylph.re> - 1.37.0-1
- Initial RPM port of the vaultwarden-deb packaging for AlmaLinux.
- Update to upstream version v1.37.0.
- Require web vault version v2026.6.4.
