#!/bin/bash
# download the repository files for Cloudflare Pages
set -e

mkdir -p repo
./sync-s3.sh s3://${AWS_S3_BUCKET}/ repo/

cp install.sh repo/install.sh

for release in 9 10 ; do
  mkdir -p repo/el/$release
  cp install.sh repo/el/$release/install.sh
  sed -i 's/EL_TARGET_VERSION=[0-9]\+/EL_TARGET_VERSION='$release'/' repo/el/$release/install.sh
done

cp 404.html repo/

cd repo/

python ../build-pages-html.py > index.html
