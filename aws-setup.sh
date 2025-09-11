#!/bin/bash

# Simple AWS EC2 Setup Script
# Installs Git, Python, and Docker only

set -e

echo "🚀 Simple AWS EC2 Setup - Git, Python, Docker"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Don't run as root. Use: sudo ./aws-setup.sh"
   exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    echo "❌ Cannot determine OS"
    exit 1
fi

echo "📋 Detected OS: $OS"

# Update system
echo "🔄 Updating system packages..."
if [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum update -y
elif [[ "$OS" == *"Ubuntu"* ]]; then
    sudo apt-get update -y
fi

# Install Git
echo "📦 Installing Git..."
if [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum install -y git
elif [[ "$OS" == *"Ubuntu"* ]]; then
    sudo apt-get install -y git
fi

# Install Python
echo "🐍 Installing Python..."
if [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum install -y python3 python3-pip
    sudo ln -sf /usr/bin/python3 /usr/bin/python
elif [[ "$OS" == *"Ubuntu"* ]]; then
    sudo apt-get install -y python3 python3-pip
    sudo ln -sf /usr/bin/python3 /usr/bin/python
fi

# Install Docker
echo "🐳 Installing Docker..."
if [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker $USER
elif [[ "$OS" == *"Ubuntu"* ]]; then
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker $USER
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Installed:"
echo "  - Git: $(git --version)"
echo "  - Python: $(python --version)"
echo "  - Docker: $(docker --version)"
echo "  - Docker Compose: $(docker-compose --version)"
echo ""
echo "⚠️  Important: Log out and log back in to use Docker without sudo"
echo "   Or run: newgrp docker"
echo ""
echo "🚀 Ready to deploy your application!"
