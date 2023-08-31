import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "requests"])

import requests
from pathlib import Path
import sys
import tempfile
import shutil
import os
from urllib.request import urlretrieve

# Set up directories
current_script_path = Path(__file__).resolve()
parent_dir = current_script_path.parent
bin_dir = parent_dir / "bin"
bin_dir.mkdir(exist_ok=True)

s7ip_dir = bin_dir / "7z"
cygwin_dir = bin_dir / "cygwin"
python_dir = bin_dir / "python"
tcc_dir = bin_dir / "tcc"
w64devkit_dir = bin_dir / "w64devkit"


def install_winpython():
    try:
        subprocess.check_output([str(python_dir / "python.exe"), "--help"])
        print("Python already installed, skipping installation.")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Python not found, proceeding with installation.")

    winpython_installer_url = "https://github.com/winpython/winpython/releases/download/6.4.20230625final/Winpython64-3.11.4.0dot.exe"

    with tempfile.TemporaryDirectory() as tmpdir:
        winpython_installer_path = Path(tmpdir) / Path(winpython_installer_url).name
        urlretrieve(winpython_installer_url, winpython_installer_path)

        with tempfile.TemporaryDirectory() as extract_temp_dir:
            subprocess.run(
                [
                    str(s7ip_dir / "7z.exe"),
                    "x",
                    str(winpython_installer_path),
                    f"-o{extract_temp_dir}",
                ]
            )

            for root, dirs, files in os.walk(extract_temp_dir):
                if "WPy64" in root and any(
                    "python" in d and "amd64" in d for d in dirs
                ):
                    python_installation_dir = (
                        Path(root)
                        / [d for d in dirs if "python" in d and "amd64" in d][0]
                    )
                    break

            shutil.copytree(python_installation_dir, python_dir)


def setup_venv():
    # Decide which Python executable to use
    try:
        subprocess.check_output([str(python_dir / "python.exe"), "--help"])
        python_executable = str(python_dir / "python.exe")
    except (FileNotFoundError, subprocess.CalledProcessError):
        python_executable = sys.executable

    venv_dir = parent_dir / "venv"
    subprocess.run([python_executable, "-m", "venv", str(venv_dir)])

    requirements_file = parent_dir / "requirements.txt"
    subprocess.run(
        [
            str(venv_dir / "Scripts" / "python.exe"),
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_file),
        ]
    )


def install_cygwin():
    # evaluate if already installed
    try:
        if "Usage: gcc" in subprocess.check_output(
            [str(cygwin_dir / "cygwin-portable.cmd"), "-c", "gcc --help"],
            stderr=subprocess.STDOUT,
        ).decode("utf-8"):
            print("Cygwin already installed, skipping installation.")
            return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("Cygwin not found, proceeding with installation.")

    # Download Cygwin portable installer
    cygwin_installer_url = "https://raw.githubusercontent.com/vegardit/cygwin-portable-installer/master/cygwin-portable-installer.cmd"
    cygwin_installer_path = cygwin_dir / "cygwin-portable-installer.cmd"
    os.makedirs(cygwin_installer_path.parent, exist_ok=True)
    with cygwin_installer_path.open("wb") as f:
        f.write(requests.get(cygwin_installer_url).content)

    # Define the essential Cygwin packages for a C project
    c_essential_packages = "gcc-core,make,gdb"

    # Modify the Cygwin installer script
    with cygwin_installer_path.open("r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("set CYGWIN_PACKAGES="):
            lines[i] = "set CYGWIN_PACKAGES=" + c_essential_packages + "\n"
            break

    with cygwin_installer_path.open("w") as f:
        f.writelines(lines)

    # Run the Cygwin installer
    subprocess.run([str(cygwin_installer_path)], cwd=str(cygwin_dir))

    # remove echos in cygwin-portable.cmd
    cygwin_portable = cygwin_dir / "cygwin-portable.cmd"
    with cygwin_portable.open("r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("echo Loading") or line.strip().startswith(
            "echo Replacing"
        ):
            lines[i] = ""

    with cygwin_portable.open("w") as f:
        f.writelines(lines)


def install_tcc():
    # Check if TCC is already installed
    try:
        if "Tiny C Compiler" in subprocess.run(
            [str(tcc_dir / "tcc.exe"), "-h"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode("utf-8"):
            print("TCC already installed, skipping installation.")
            return
    except FileNotFoundError:
        pass

    print("TCC not found, proceeding with installation.")

    # Download TCC ZIP to a temporary location
    tcc_zip_url = (
        "http://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win64-bin.zip"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tcc_zip_path = Path(tmpdir) / Path(tcc_zip_url).name
        urlretrieve(tcc_zip_url, tcc_zip_path)

        # Extract TCC ZIP to `tcc_dir`
        subprocess.run(
            [str(s7ip_dir / "7z.exe"), "x", str(tcc_zip_path), f"-o{tcc_dir.parent}"]
        )


def install_w64devkit():
    try:
        if "Usage: gcc" in subprocess.check_output(
            [str(w64devkit_dir / "bin" / "gcc.exe"), "--help"],
            stderr=subprocess.STDOUT,
        ).decode("utf-8"):
            print("w64devkit already installed, skipping installation.")
            return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("w64devkit not found, proceeding with installation.")

    # Download w64devkit ZIP to a temporary location
    w64devkit_zip_url = "https://github.com/skeeto/w64devkit/releases/download/v1.20.0/w64devkit-1.20.0.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        w64devkit_zip_path = Path(tmpdir) / Path(w64devkit_zip_url).name
        urlretrieve(w64devkit_zip_url, w64devkit_zip_path)

        # Extract w64devkit ZIP to `w64devkit_dir`
        subprocess.run(
            [
                str(s7ip_dir / "7z.exe"),
                "x",
                str(w64devkit_zip_path),
                f"-o{w64devkit_dir.parent}",
            ]
        )


# Now you can install all dependencies for this project
if __name__ == "__main__":
    
    # install_winpython()
    # install_cygwin()
    # install_tcc()

    setup_venv()
    install_w64devkit()
