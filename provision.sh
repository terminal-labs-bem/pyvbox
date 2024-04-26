DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
apt-get install -y -q

apt-get update -y
apt-get upgrade -y

apt-get install build-essential -y
apt-get install curl -y
apt-get install git -y

apt-get install pipx -y
pipx ensurepath

curl -sSf https://rye-up.com/get | RYE_HOME=/opt/rye RYE_VERSION="0.32.0" RYE_TOOLCHAIN_VERSION="3.11.8" RYE_INSTALL_OPTION="--yes" bash &> /dev/null
cat > /usr/local/bin/rye <<EOF
#!/bin/sh
RUSTUP_HOME=/opt/rye exec /opt/rye/shims/\${0##*/} "\$@"
EOF
chmod +x /usr/local/bin/rye
rye config --set-bool behavior.global-python=false

su - vagrant << EOF
curl -sSf https://rye-up.com/get | RYE_VERSION="0.32.0" RYE_TOOLCHAIN_VERSION="3.11.8" RYE_INSTALL_OPTION="--yes" bash &> /dev/null
rye config --set-bool behavior.global-python=false
EOF
