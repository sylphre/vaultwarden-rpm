# https://docs.fedoraproject.org/en-US/quick-docs/adding-or-removing-software-repositories-in-fedora/
# based on code from https://github.com/retorquere/zotero-deb

case `uname -m` in
  "x86_64")
    ;;
  *)
    echo "Vaultwarden is only compiled for the x86_64 architecture"
    exit
    ;;
esac

EL_TARGET_VERSION=9
BASEURL=https://vaultwarden-rpm.pages.dev
KEYNAME=RPM-GPG-KEY-vaultwarden-rpm
GPGKEY=$BASEURL/$KEYNAME
KEYRING=/etc/pki/rpm-gpg/$KEYNAME

sudo mkdir -p /etc/pki/rpm-gpg
if [ -x "$(command -v curl)" ]; then
  sudo curl -L $GPGKEY -o $KEYRING
elif [ -x "$(command -v wget)" ]; then
  sudo wget -O $KEYRING $GPGKEY
else
  echo "Error: need wget or curl installed." >&2
  exit 1
fi

sudo chmod 644 $KEYRING
sudo rpm --import $KEYRING

# \$basearch stays unexpanded on purpose: dnf resolves it at run time.
cat << EOF | sudo tee /etc/yum.repos.d/vaultwarden-rpm.repo
[vaultwarden]
name=Vaultwarden RPM repository (EL ${EL_TARGET_VERSION})
baseurl=$BASEURL/el/$EL_TARGET_VERSION/\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=file://$KEYRING
EOF

sudo dnf clean all
