# Sky Warr

A space shooter game with both single-player and multiplayer modes.

## Prerequisites

- Python 3.7 or higher
- Pygame 2.0.0 or higher
- Pillow (PIL) 8.0.0 or higher

## Installation

### Method 1: Install with pip

```bash
pip install .
```

### Method 2: Build standalone executable

First, make sure you have PyInstaller installed:

```bash
pip install pyinstaller
```

Then run the build script:

```bash
python build.py
```

This will:

1. Create game assets if they don't exist
2. Build a standalone executable package in the `dist/SkyWarr` directory
3. Create an installer appropriate for your platform (Windows .exe or Linux .deb)

#### Linux Requirements for Creating .deb Package

On Linux, to create a .deb package, you need the `dpkg-dev` package:

```bash
sudo apt-get install dpkg-dev
```

#### Windows Requirements for Creating Installer

On Windows, to create an installer, you need NSIS (Nullsoft Scriptable Install System):

1. Download and install from: https://nsis.sourceforge.io/Download
2. Make sure it's installed in the default location (C:/Program Files/NSIS or C:/Program Files (x86)/NSIS)

## Running the Game

### If installed via pip:

```bash
skywarr
```

### If using the standalone executable:

- On Windows: Run `SkyWarr.exe` from the installation directory
- On Linux: Run `skywarr` from the terminal

## Game Controls

- Arrow keys or A/D: Move the spaceship left and right
- Space: Fire
- Escape: Exit the game
- R: Restart (single-player mode only, after game over)

## Multiplayer Mode

The game supports two players playing over a network:

1. One player hosts the game (selects "Host Multiplayer")
2. The other player joins (selects "Join Multiplayer" and enters the host's IP address)

Both players must be able to establish a connection on port 5555.
