#!/bin/bash
set -e
set -x

SOURCE_URL=https://github.com/dani-garcia/vaultwarden/archive/refs/tags/${VW_SERVER_VERSION}.tar.gz
BASE_IMAGE=almalinux:${ALMA_TARGET_VERSION}
RUST_VERSION=${RUST_VERSION:-1.89.0}

# download latest source
wget -O vaultwarden.tar.gz $SOURCE_URL

# build docker image
docker build --build-arg base_image=$BASE_IMAGE \
             --build-arg rust_version=$RUST_VERSION \
             -t vaultwarden-rpm .

# extract files
docker create --name vw vaultwarden-rpm
docker cp vw:/out .
docker rm vw
docker image rm vaultwarden-rpm

# rpmbuild writes to <_rpmdir>/<arch>/
mv out/x86_64/vaultwarden-*.rpm .
