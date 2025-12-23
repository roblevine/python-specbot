#!/bin/sh
echo "starting installation script"

echo "update and install apt packages"
sudo apt update
sudo apt upgrade -y
sudo apt install -y vim iputils-ping dos2unix

# Create symlink for libcrypt on ARM machines
if [ "$(uname -m)" = "aarch64" ]; then
    echo "Setting up libcrypt symlink for ARM64"
    sudo mkdir -p /usr/lib/aarch64-linux-gnu
    sudo ln -sf /usr/lib/aarch64-linux-gnu/libcrypt.so.1 /usr/lib/aarch64-linux-gnu/libcrypt-c6b9afc0.so.1
fi

echo "setting up Rob public key for ssh access"
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDGwG5A7UQ4vQSM/SEn1ndXfgOO2RoeARNsOpnIr80du rob levine@ANOMALY" >> ~/.ssh/authorized_keys

echo "installation script complete"
