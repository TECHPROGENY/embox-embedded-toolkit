#!/usr/bin/env python3

import os
import platform
import subprocess
import sys

# Check for Python 3.10
if not subprocess.run(["python3.10", "--version"], capture_output=True, text=True).stdout.startswith("Python 3.10"):
    # Install Python 3.10 from package manager
    if platform.system() == "Linux":
        # Debian/Ubuntu
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3.10"])
    elif platform.system() == "Darwin":
        # macOS with Homebrew
        subprocess.run(["brew", "install", "python@3.10"])
    elif platform.system() == "Windows":
        # Windows with Chocolatey
        subprocess.run(["choco", "install", "python310"])
    else:
        print("Unsupported operating system")
        sys.exit(1)

# Install Git
if not subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.startswith("git version"):
    if platform.system() == "Linux":
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "git"])
    elif platform.system() == "Darwin":
        subprocess.run(["brew", "install", "git"])
    elif platform.system() == "Windows":
        print("Git not found")
    else:
        print("Unsupported operating system")
        sys.exit(1)

# Install Python packages with pip
subprocess.run(["pip3.10", "install", "pyqt6", "requests", "paho-mqtt", "pyqtgraph", "qt_material"])

# Install Mosquitto broker package if not installed
if not subprocess.run(["which", "mosquitto"], capture_output=True, text=True).stdout:
    if platform.system() == "Linux":
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "mosquitto"])
    elif platform.system() == "Darwin":
        subprocess.run(["brew", "install", "mosquitto"])
    elif platform.system() == "Windows":
        subprocess.run(["choco", "install", "mosquitto"])
    else:
        print("Unsupported operating system")
        sys.exit(1)

# Clone the GitHub repo to ~/mbox and make scripts executable
os.makedirs(os.path.expanduser("~/mbox"), exist_ok=True)
subprocess.run(["git", "clone", "https://github.com/username/repo.git", os.path.expanduser("~/mbox")])
subprocess.run(["chmod", "+x", os.path.expanduser("~/mbox/*.sh")])

# Set environment path for mbox.py globally
if platform.system() == "Linux":
    with open(os.path.expanduser("~/.bashrc"), "a") as bashrc:
        bashrc.write('export PATH="$PATH:$HOME/mbox"\n')
    os.system("source ~/.bashrc")
elif platform.system() == "Darwin":
    with open(os.path.expanduser("~/.bash_profile"), "a") as bash_profile:
        bash_profile.write('export PATH="$PATH:$HOME/mbox"\n')
    os.system("source ~/.bash_profile")
elif platform.system() == "Windows":
    subprocess.run(["setx", "/M", "PATH", "%PATH%;%USERPROFILE%\\mbox"])
else:
    print("Unsupported operating system")
    sys.exit(1)
