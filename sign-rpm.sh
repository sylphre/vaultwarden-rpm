#!/bin/bash -e
# Sign RPM packages with the repository key.
#
#   GPG_KEY_ID=... GPG_PASSPHRASE=... ./sign-rpm.sh pkg1.rpm pkg2.rpm

WORKDIR=$(mktemp -d)
trap 'rm -rf "${WORKDIR}"' EXIT

# The passphrase goes through a 0600 file rather than the command line,
# so it never shows up in the process list.
printf '%s' "${GPG_PASSPHRASE}" > "${WORKDIR}/passphrase"
chmod 600 "${WORKDIR}/passphrase"

rpmsign --define "_gpg_name ${GPG_KEY_ID}" \
        --define "_gpg_digest_algo sha256" \
        --define "_gpg_sign_cmd_extra_args --batch --yes --pinentry-mode loopback --passphrase-file ${WORKDIR}/passphrase" \
        --addsign "$@"

# Verify against a throwaway rpmdb holding just our public key. The build
# host's own rpmdb has never seen this key, so a plain --checksig there
# reports "SIGNATURES NOT OK" even for a perfectly signed package.
gpg --batch --armor --export "${GPG_KEY_ID}" > "${WORKDIR}/pubkey.asc"
rpm --dbpath "${WORKDIR}/rpmdb" --initdb
rpm --dbpath "${WORKDIR}/rpmdb" --import "${WORKDIR}/pubkey.asc"
rpm --dbpath "${WORKDIR}/rpmdb" --checksig "$@"
