import os
import sys
import shutil
import subprocess
import platform

def detect_platform():
    """Detect the current platform"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"

def create_assets():
    """Create game assets if they don't exist"""
    if not os.path.exists("assets/images/menu_bg.jpg"):
        print("Creating game assets...")
        from create_assets import create_directories, create_menu_bg, create_sky_bg
        from create_assets import create_player, create_enemy, create_cloud
        create_directories()
        create_menu_bg()
        create_sky_bg()
        create_player()
        create_enemy()
        create_cloud()

def build_with_pyinstaller(current_platform):
    """Build executable with PyInstaller"""
    # Make sure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Set console mode based on platform
    if current_platform == "windows":
        console_mode = "False"
    else:
        console_mode = "True"
    
    # Create the spec file for PyInstaller
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('assets', 'assets')],
             hiddenimports=['PIL._tkinter_finder'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SkyWarr',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console={console_mode})
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SkyWarr')
"""
    
    # Write spec file
    with open("skywarr.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    print(f"Building executable for {current_platform}...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "skywarr.spec", 
        "--clean"
    ])
    
    print(f"Build complete! Executable is in the dist/SkyWarr directory.")

def create_linux_installer():
    """Create a .deb package for Linux"""
    print("Creating Linux installer...")
    
    # Create directory structure for .deb package (excluding DEBIAN for now)
    os.makedirs("deb_dist/skywarr/usr/bin", exist_ok=True)
    os.makedirs("deb_dist/skywarr/usr/share/applications", exist_ok=True)
    
    # Make sure the destination directory is clean
    skywarr_share_dir = "deb_dist/skywarr/usr/share/skywarr"
    if os.path.exists(skywarr_share_dir):
        print("Removing existing directory:", skywarr_share_dir)
        shutil.rmtree(skywarr_share_dir)
    
    # Now create the directory and then copy
    os.makedirs(skywarr_share_dir, exist_ok=True)
    
    # Copy executable and assets
    print("Copying files from dist/SkyWarr to", skywarr_share_dir)
    for item in os.listdir("dist/SkyWarr"):
        s = os.path.join("dist/SkyWarr", item)
        d = os.path.join(skywarr_share_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    
    # Create launcher script
    with open("deb_dist/skywarr/usr/bin/skywarr", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("cd /usr/share/skywarr\n")
        f.write("./SkyWarr \"$@\"\n")
    
    # Make launcher executable
    os.chmod("deb_dist/skywarr/usr/bin/skywarr", 0o755)
    
    # Create desktop entry
    with open("deb_dist/skywarr/usr/share/applications/skywarr.desktop", "w") as f:
        f.write("[Desktop Entry]\n")
        f.write("Name=Sky Warr\n")
        f.write("Comment=Space shooter game\n")
        f.write("Exec=skywarr\n")
        f.write("Terminal=false\n")
        f.write("Type=Application\n")
        f.write("Categories=Game;ArcadeGame;\n")
    
    # Fix permissions for directories
    for root, dirs, files in os.walk("deb_dist/skywarr"):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            filepath = os.path.join(root, f)
            # Executables in bin should be executable
            if "/usr/bin/" in filepath:
                os.chmod(filepath, 0o755)
            else:
                os.chmod(filepath, 0o644)
    
    # Now handle the DEBIAN directory specially - completely recreate it
    debian_dir = "deb_dist/skywarr/DEBIAN"
    if os.path.exists(debian_dir):
        print(f"Removing existing DEBIAN directory: {debian_dir}")
        shutil.rmtree(debian_dir)
    
    # Create the DEBIAN directory with correct permissions
    print("Creating new DEBIAN directory with correct permissions")
    # Use os.mkdir instead of os.makedirs to have more direct control
    os.mkdir(debian_dir, mode=0o755)
    
    # Create control file with correct permissions
    control_file = os.path.join(debian_dir, "control")
    with open(control_file, "w") as f:
        f.write("Package: skywarr\n")
        f.write("Version: 1.0.0\n")
        f.write("Section: games\n")
        f.write("Priority: optional\n")
        f.write("Architecture: amd64\n")
        f.write("Maintainer: SkyWarr Developer <developer@example.com>\n")
        f.write("Description: Space shooter game with single and multiplayer modes\n")
    
    os.chmod(control_file, 0o644)
    
    fix_debian_permissions(debian_dir)
    
    # Check permissions before building
    debian_perms = oct(os.stat(debian_dir).st_mode & 0o755)
    control_perms = oct(os.stat(control_file).st_mode & 0o775)
    print(f"DEBIAN directory permissions: {debian_perms}")
    print(f"control file permissions: {control_perms}")
    
    # Build .deb package
    print("Building .deb package...")
    try:
        subprocess.check_call([
            "dpkg-deb", 
            "--build", 
            "deb_dist/skywarr", 
            "deb_dist/skywarr_1.0.0_amd64.deb"
        ])
        print("Linux .deb package created in deb_dist/ directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error building package: {e}")
        # Try one more time with explicit umask
        old_umask = os.umask(0o022)  # Set umask to ensure correct permissions
        try:
            print("Retrying with explicit umask...")
            subprocess.check_call([
                "dpkg-deb", 
                "--build", 
                "deb_dist/skywarr", 
                "deb_dist/skywarr_1.0.0_amd64.deb"
            ])
            print("Linux .deb package created in deb_dist/ directory.")
        finally:
            os.umask(old_umask)

def fix_debian_permissions(debian_dir):
    os.chmod(debian_dir, 0o755)
    for root, dirs, files in os.walk(debian_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)

def create_windows_installer():
    """Create a Windows installer using NSIS"""
    print("Creating Windows installer...")
    
    # Check if NSIS is installed
    nsis_path = None
    if os.path.exists("C:/Program Files (x86)/NSIS/makensis.exe"):
        nsis_path = "C:/Program Files (x86)/NSIS/makensis.exe"
    elif os.path.exists("C:/Program Files/NSIS/makensis.exe"):
        nsis_path = "C:/Program Files/NSIS/makensis.exe"
    
    if not nsis_path:
        print("NSIS not found. Please install it from https://nsis.sourceforge.io/Download")
        print("After installing, run this script again.")
        return
    
    # Create NSIS script
    with open("installer.nsi", "w") as f:
        f.write("""
; SkyWarr Windows Installer Script

!include "MUI2.nsh"

; General settings
Name "Sky Warr"
OutFile "SkyWarr_Setup.exe"
InstallDir "$PROGRAMFILES\\SkyWarr"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy files
  File /r "dist\\SkyWarr\\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\\SkyWarr"
  CreateShortcut "$SMPROGRAMS\\SkyWarr\\SkyWarr.lnk" "$INSTDIR\\SkyWarr.exe"
  CreateShortcut "$DESKTOP\\SkyWarr.lnk" "$INSTDIR\\SkyWarr.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  
  ; Create registry entries
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SkyWarr" "DisplayName" "Sky Warr"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SkyWarr" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\\SkyWarr\\SkyWarr.lnk"
  RMDir "$SMPROGRAMS\\SkyWarr"
  Delete "$DESKTOP\\SkyWarr.lnk"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SkyWarr"
SectionEnd
""")
    
    # Run NSIS
    subprocess.check_call([nsis_path, "installer.nsi"])
    
    print("Windows installer created: SkyWarr_Setup.exe")

def main():
    current_platform = detect_platform()
    print(f"Detected platform: {current_platform}")
    
    # First make sure we have the assets
    create_assets()
    
    # Build the executable
    build_with_pyinstaller(current_platform)
    
    # Create platform-specific installer
    if current_platform == "linux":
        try:
            create_linux_installer()
        except Exception as e:
            print(f"Error creating Linux installer: {e}")
            print("You may need to install dpkg-deb: sudo apt-get install dpkg-dev")
    elif current_platform == "windows":
        try:
            create_windows_installer()
        except Exception as e:
            print(f"Error creating Windows installer: {e}")
            print("Make sure NSIS is installed: https://nsis.sourceforge.io/Download")
    else:
        print(f"No installer support for platform: {current_platform}")

if __name__ == "__main__":
    main()
