# RPM counterpart of the former debian/ directory.
#
# The web vault is a prebuilt tarball from bw_web_builds: the Makefile fetches
# it and the install section only unpacks it. rpmbuild runs with
# --build-in-place, so the build directory is the checkout and the downloaded
# tarball is found there.
#
# Note: keep section names out of comments, rpm parses them as section
# markers even behind a hash.

Name:           vaultwarden-web-vault
Version:        2026.6.4
Release:        1%{?dist}
Summary:        Web vault for the Vaultwarden server

License:        GPL-3.0-only
URL:            https://github.com/dani-garcia/bw_web_builds
Source0:        %{url}/releases/download/v%{version}/bw_web_v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  tar

%description
The Bitwarden web vault, patched for use with the Vaultwarden server.

%build
# Nothing to do: the tarball is prebuilt upstream.

%install
%make_install DATADIR=%{_datadir} VW_WEB_VERSION=v%{version}

%files
%dir %{_datadir}/vaultwarden
%{_datadir}/vaultwarden/web-vault

%changelog
* Sat Jul 25 2026 Laurier Sylph. <laurier@sylph.re> - 2026.6.4-1
- Initial RPM port of the vaultwarden-deb packaging for AlmaLinux.
- Update to upstream version v2026.6.4.
