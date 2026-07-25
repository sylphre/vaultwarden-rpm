# Vaultwarden rpm packages

This repository contains rpm packages of [Vaultwarden](https://github.com/dani-garcia/vaultwarden), a Bitwarden-compatible API server written in Rust. They can be installed in AlmaLinux and other Enterprise Linux rebuilds (Rocky Linux, RHEL, Oracle Linux).

It is a port of [gvtulder/vaultwarden-deb](https://github.com/gvtulder/vaultwarden-deb) to rpm, keeping the same repository layout: the `debian/` directories are replaced by `rpm/` directories holding a spec file, and `dpkg-buildpackage` by `rpmbuild --build-in-place`. The published repository lives on GitHub Pages (`gh-pages` branch) instead of S3 + Cloudflare Pages.

The server binary is compiled from the upstream sources inside an AlmaLinux container, so it links against the DB client libraries of the target release.

See the [Vaultwarden](https://github.com/dani-garcia/vaultwarden) repository for much more information.

## Contents

The repository provides two packages:

* `vaultwarden`, the main executable, from [dani-garcia/vaultwarden](https://github.com/dani-garcia/vaultwarden);
* `vaultwarden-web-vault`, the Bitwarden web vault, from [dani-garcia/bw_web_builds](https://github.com/dani-garcia/bw_web_builds).

Use `dnf install vaultwarden` to install both.

## Installation

To install Vaultwarden and add this repository, run this for AlmaLinux 9:
```bash
curl -sSfL https://sylphre.github.io/vaultwarden-rpm/el/9/install.sh | sudo bash
sudo dnf install vaultwarden
```

For AlmaLinux 10:
```bash
curl -sSfL https://sylphre.github.io/vaultwarden-rpm/el/10/install.sh | sudo bash
sudo dnf install vaultwarden
```

The packages can also be downloaded manually from the [repository web page](https://sylphre.github.io/vaultwarden-rpm/).

## Important configuration

After installation, Vaultwarden needs to be configured. Edit the configuration file at `/etc/vaultwarden.env` to change important settings, such as the port number, the database, and security options.

The file is mode `0640`, owned by `root:vaultwarden`, because it holds `ADMIN_TOKEN` and SMTP credentials. Edit it as root.

Vaultwarden is added to `systemd` and can be started and stopped with:
```bash
sudo systemctl status vaultwarden
# to start and stop
sudo systemctl start vaultwarden
sudo systemctl stop vaultwarden
# to start on boot
sudo systemctl enable vaultwarden
```

If `firewalld` is running, open the port Vaultwarden listens on:
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### Directories

The packages add the following files:
* `/etc/vaultwarden.env`: the configuration file.
* `/etc/logrotate.d/vaultwarden`: the log rotation rules.
* `/usr/bin/vaultwarden`: the Vaultwarden server.
* `/usr/lib/systemd/system/vaultwarden.service`: the systemd unit.
* `/usr/share/vaultwarden/web-vault`: the files for the Bitwarden web vault.
* `/var/lib/vaultwarden/data`: the data directory.
* `/var/log/vaultwarden`: the log file.

### SELinux

The service runs unconfined under the default targeted policy, so no extra
labelling is needed for the paths above. If you move `DATA_FOLDER` or
`LOG_FILE` elsewhere, relabel the new location or the confined systemd
sandbox directives in the unit (`ProtectSystem=strict`, `ReadWritePaths=`)
will deny the writes.

## Building

Both packages are built by the `build.yaml` workflow, but can be built by hand:

```bash
# server: compiles vaultwarden in an almalinux:9 container, then runs rpmbuild
cd vaultwarden/
VW_SERVER_VERSION=v1.37.0 ALMA_TARGET_VERSION=9 ./build-in-docker.sh

# web vault: downloads the prebuilt tarball and packages it (noarch)
cd vaultwarden-web-vault/
VW_WEB_VERSION=v2026.6.4 make rpm DIST=.el9
```

`generate-files.py` bumps `Version:`, resets `Release:` and prepends a
`%changelog` entry in both spec files when upstream publishes a new release.

## Repository setup

The `build.yaml` workflow needs two secrets and one repository setting:

| Secret | Contents |
| --- | --- |
| `GPG_PRIVATE_KEY` | ASCII-armored private signing key |
| `GPG_PASSPHRASE` | Its passphrase |

Both the rpm files (`rpmsign --addsign`) and the repository metadata
(`repodata/repomd.xml.asc`) are signed with that key, which is why the
generated `install.sh` sets both `gpgcheck=1` and `repo_gpgcheck=1`.

The `publish` job force-pushes the finished repository tree to the `gh-pages`
branch, one commit per run. Set **Settings > Pages > Source** to *Deploy from a
branch*, `gh-pages` / `/ (root)`.
