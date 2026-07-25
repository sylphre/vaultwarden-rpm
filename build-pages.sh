#!/bin/bash
# assemble the files served by GitHub Pages, in place, from the gh-pages tree
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_DIR=$(cd "${1:-repo}" && pwd)
BASEURL=${PAGES_URL:-https://sylphre.github.io/vaultwarden-rpm}

install_script() {
  # $1: destination, $2: EL version to pin
  cp "$SCRIPT_DIR/install.sh" "$1"
  sed -i 's/^EL_TARGET_VERSION=[0-9]\+/EL_TARGET_VERSION='"$2"'/' "$1"
  # point the copy at wherever this repository is actually published
  sed -i "s|^BASEURL=.*|BASEURL=$BASEURL|" "$1"
}

install_script "$REPO_DIR/install.sh" 9

for release in 9 10 ; do
  [ -d "$REPO_DIR/el/$release" ] || continue
  install_script "$REPO_DIR/el/$release/install.sh" "$release"
done

cp "$SCRIPT_DIR/404.html" "$REPO_DIR/"
# keep Pages from running the tree through Jekyll
touch "$REPO_DIR/.nojekyll"

cd "$REPO_DIR"
python3 "$SCRIPT_DIR/build-pages-html.py" > index.html
