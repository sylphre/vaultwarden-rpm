#!/bin/bash
set -e
set -x

SOURCE_URL=https://github.com/dani-garcia/vaultwarden/archive/refs/tags/${VW_SERVER_VERSION}.tar.gz
RUST_VERSION=${RUST_VERSION:-1.89.0}

# AlmaLinux publishes the same images to several registries. Docker Hub is
# tried last: it rate-limits anonymous pulls and regularly times out from CI.
ALMA_REGISTRIES=${ALMA_REGISTRIES:-"quay.io/almalinuxorg/almalinux public.ecr.aws/almalinux/almalinux docker.io/library/almalinux"}

# download latest source
wget -O vaultwarden.tar.gz $SOURCE_URL

# pull the base image, trying each registry twice before moving on
BASE_IMAGE=
for registry in $ALMA_REGISTRIES ; do
  for attempt in 1 2 ; do
    if docker pull "${registry}:${ALMA_TARGET_VERSION}" ; then
      BASE_IMAGE="${registry}:${ALMA_TARGET_VERSION}"
      break 2
    fi
    sleep $(( attempt * 10 ))
  done
done

if [ -z "$BASE_IMAGE" ] ; then
  echo "Error: could not pull almalinux:${ALMA_TARGET_VERSION} from any registry." >&2
  exit 1
fi

# build docker image
# --pull=false: the base image is already in the local store, so the build
# does not have to reach the registry again
docker build --pull=false \
             --build-arg base_image=$BASE_IMAGE \
             --build-arg rust_version=$RUST_VERSION \
             -t vaultwarden-rpm .

# extract files
docker create --name vw vaultwarden-rpm
docker cp vw:/out .
docker rm vw
docker image rm vaultwarden-rpm

# rpmbuild writes to <_rpmdir>/<arch>/
mv out/x86_64/vaultwarden-*.rpm .
