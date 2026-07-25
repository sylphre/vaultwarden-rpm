import datetime
import glob
import re
import os.path


# generates the index page for the repository


EL_RELEASES = {
    "10": { "name": "AlmaLinux 10", "archived": False },
    "9": { "name": "AlmaLinux 9", "archived": False },
}
ARCHITECTURES = [ "x86_64" ]
# vaultwarden-web-vault is noarch, but published next to the x86_64 packages
PACKAGE_ARCH = { "vaultwarden": "x86_64", "vaultwarden-web-vault": "noarch" }

IGNORED_PATHS = set([ "repodata", "index.html", "404.html" ])


def version_key(filename):
    """Sort key over the version-release part of an rpm file name."""
    m = re.match(r".+-([^-]+-[^-]+)\.[^.]+\.rpm$", os.path.basename(filename))
    text = m[1] if m else os.path.basename(filename)
    # numeric runs sort above alphabetic ones, roughly like rpmvercmp
    return [(1, int(p)) if p.isdigit() else (0, p)
            for p in re.findall(r"[0-9]+|[a-zA-Z]+", text)]


latest_versions = {}
for release in EL_RELEASES:
    for arch in ARCHITECTURES:
        latest_versions[(release, arch)] = [
            sorted(glob.glob(f"el/{release}/{arch}/{package}-[0-9]*.{PACKAGE_ARCH[package]}.rpm"),
                   key=version_key)[-1]
            for package in ("vaultwarden", "vaultwarden-web-vault")
        ]


print("""
<!doctype html>
<html>
  <head><title>Vaultwarden rpm repository</title>
  <style type="text/css">
body {
  font-family: sans-serif;
  font-size: 14px;
}
a {
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

.latest-releases {
  padding: 0;
  margin: 0;
}
.latest-releases th,
.latest-releases td {
  padding: 5px 8px;
  margin: 0;
  text-align: left;
  font-size: 14px;
}
.latest-releases .current th,
.latest-releases .current td {
  background: #eee;
}
.latest-releases .arch {
  font-weight: normal;
}

.all-files,
.all-files li,
.all-files ul {
  margin: 0;
  padding: 3px 0;
  text-indent: 0;
  list-style: none;
}
.all-files > li {
  margin-right: 60px;
}
.all-files li li {
  margin-left: 25px;
}
  </style>
</head>
<body>
<h1>Vaultwarden rpm repository</h1>
<p>
This repository contains rpm packages of Vaultwarden, a Bitwarden-compatible API server written in Rust. They can be installed in AlmaLinux and other Enterprise Linux rebuilds.
</p>
<p>
See the <a href="https://github.com/sylphre/vaultwarden-rpm/">GitHub repository</a> for more information.
</p>

<hr>

<h2>Latest release</h2>
<table class="latest-releases">
""")


for idx, ((release, arch), files) in enumerate(latest_versions.items()):
    print('  <tr class="current">')
    print(f'    <th class="release">{EL_RELEASES[release]["name"]} (el{release})</th>')
    if EL_RELEASES[release]["archived"]:
        print(f'    <th>archived</th>')
    else:
        print(f'    <th></th>')
    print(f'    <th class="arch">{arch}</th>')
    for file in files:
        print(f'    <td><a href="{file}">{os.path.basename(file)}</a></td>')
    print("  </tr>")


print("""
</table>
<p>
Repository updated on """ + datetime.datetime.now().strftime('%Y.%m.%d') + """.
</p>

<hr>

<h2>Installing the repository</h2>
""")


for release, info in EL_RELEASES.items():
    if not info["archived"]:
        print("""
<p>To install Vaultwarden and add this repository, run this for """ + f'{info["name"]} (el{release})' + """:</p>
<pre>
curl -sSfL https://vaultwarden-rpm.pages.dev/el/""" + release + """/install.sh | sudo bash
sudo dnf install vaultwarden
</pre>
""")

print("""
<hr>

<h2>All files</h2>
<ul class="all-files">
""")


def print_file_tree(path=".", indent=""):
    with os.scandir(path) as it:
        for entry in sorted(it, key=lambda e: (e.is_dir(), e.name)):
            if entry.name in IGNORED_PATHS:
                pass
            elif entry.is_dir():
                print(f'{indent}<li>{entry.name}')
                print(f'{indent} <ul>')
                print_file_tree(entry.path, indent + "  ")
                print(f'{indent} </ul>')
                print(f"{indent}</li>")
            else:
                print(f'{indent}<li><a href="{entry.path}">{entry.name}</a></li>')


print_file_tree()

print("""
</ul>

</html>
""")
