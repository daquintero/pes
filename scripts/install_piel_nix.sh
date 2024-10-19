echo "Downloading nix with extra options:"
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix/pr/1145 | sh -s -- install --no-confirm --extra-conf "
    extra-substituters = https://openlane.cachix.org
    extra-trusted-public-keys = openlane.cachix.org-1:qqdwh+QMNGmZAuyeQJTH9ErW57OWSvdtuwfBKdS254E=
"
echo "Creating nix-flake configuration"
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
echo "Building piel-nix environment"
nix build .
