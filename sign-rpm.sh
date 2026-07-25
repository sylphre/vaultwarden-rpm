#!/bin/bash -e
# Sign RPM packages with the repository key.
#
#   GPG_KEY_ID=... GPG_PASSPHRASE=... ./sign-rpm.sh pkg1.rpm pkg2.rpm
#
# The passphrase goes through a 0600 temp file rather than the command line,
# so it never shows up in the process list.

PASSPHRASE_FILE=$(mktemp)
chmod 600 "${PASSPHRASE_FILE}"
trap 'rm -f "${PASSPHRASE_FILE}"' EXIT
printf '%s' "${GPG_PASSPHRASE}" > "${PASSPHRASE_FILE}"

rpmsign --define "_gpg_name ${GPG_KEY_ID}" \
        --define "_gpg_digest_algo sha256" \
        --define "_gpg_sign_cmd_extra_args --batch --yes --pinentry-mode loopback --passphrase-file ${PASSPHRASE_FILE}" \
        --addsign "$@"

rpm --checksig "$@"
