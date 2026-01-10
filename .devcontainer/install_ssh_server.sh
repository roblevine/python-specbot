#!/bin/sh
# SSH server setup for devcontainer
# Reads SSH_HOST_ED25519_KEY and SSH_AUTHORIZED_KEY from environment
# (set via .env_devcontainer)

echo "** configuring SSH server"

# Ensure openssh-server is installed
if ! command -v sshd > /dev/null 2>&1; then
    echo "*** installing openssh-server"
    sudo apt update && sudo apt install -y openssh-server
fi

# Configure SSH for key-based auth only
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Remove the HOME=/root line from /etc/environment - this screws up SSH sessions
sudo sed -i '/^HOME=/d' /etc/environment

# Install host keys from environment variable
# Note: newlines in the key are stored as | characters in .env_devcontainer
if [ -n "$SSH_HOST_ED25519_KEY" ]; then
    echo "*** installing SSH host key from environment"
    echo "$SSH_HOST_ED25519_KEY" | tr '|' '\n' | sudo tee /etc/ssh/ssh_host_ed25519_key > /dev/null
    sudo chmod 600 /etc/ssh/ssh_host_ed25519_key
    
    # Generate public key from private key
    sudo ssh-keygen -y -f /etc/ssh/ssh_host_ed25519_key | sudo tee /etc/ssh/ssh_host_ed25519_key.pub > /dev/null
    sudo chmod 644 /etc/ssh/ssh_host_ed25519_key.pub
else
    echo "*** WARNING: SSH_HOST_ED25519_KEY not set - generating new host key"
    echo "*** You will get known_hosts warnings on rebuild unless you add the key to .env_devcontainer"
    sudo ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""
    echo ""
    echo "*** To persist this host key, add the following to .env_devcontainer:"
    echo "SSH_HOST_ED25519_KEY=$(sudo cat /etc/ssh/ssh_host_ed25519_key | tr '\n' '|')"
    echo ""
fi

# Set up authorized_keys for vscode user
echo "*** setting up SSH authorized_keys for vscode user"
mkdir -p /home/vscode/.ssh
chmod 700 /home/vscode/.ssh

# Create environment file for SSH sessions to match VS Code terminal
cat > /home/vscode/.ssh/environment << 'EOF'
SHELL=/bin/bash
EOF

# Enable environment processing in SSH
sudo sed -i 's/#PermitUserEnvironment no/PermitUserEnvironment yes/' /etc/ssh/sshd_config

# Ensure vscode user's .bashrc is sourced for interactive SSH sessions
# Copy the devcontainer bash prompt setup if not already present
if ! grep -q "devcontainer" /home/vscode/.bashrc 2>/dev/null; then
    cat >> /home/vscode/.bashrc << 'EOF'

# Load devcontainer bash prompt if available
if [ -f /usr/local/share/bash-prompt/bash-prompt.sh ]; then
    source /usr/local/share/bash-prompt/bash-prompt.sh
fi
EOF
fi

if [ -n "$SSH_AUTHORIZED_KEY" ]; then
    echo "$SSH_AUTHORIZED_KEY" > /home/vscode/.ssh/authorized_keys
    chmod 600 /home/vscode/.ssh/authorized_keys
    echo "*** authorized_keys installed successfully"
else
    echo "*** WARNING: SSH_AUTHORIZED_KEY not set in .env_devcontainer"
    echo "*** SSH key auth will not work until you add your public key"
fi

chown vscode:vscode /home/vscode/.bashrc
chown -R vscode:vscode /home/vscode/.ssh

# Set default working directory for SSH sessions
if ! grep -q "cd /workspaces" /home/vscode/.bashrc 2>/dev/null; then
    cat >> /home/vscode/.bashrc << 'EOF'

# Default to workspace directory if it exists
if [ -d /workspaces ] && [ "$(pwd)" = "$HOME" ]; then
    cd /workspaces/* 2>/dev/null || true
fi
EOF
fi