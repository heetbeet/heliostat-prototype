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
cygwin_dir = bin_dir / "cygwin"
python_dir = bin_dir / "python"
s7ip_dir = bin_dir / "7z"


def install_winpython():
    try:
        subprocess.check_output([str(python_dir / "python.exe"), "--help"])
        print("Python already installed, skipping installation.")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Python not found, proceeding with installation.")

    # Download WinPython installer to a temporary location
    winpython_installer_url = "https://github.com/winpython/winpython/releases/download/6.4.20230625final/Winpython64-3.11.4.0dot.exe"

    with tempfile.TemporaryDirectory() as tmpdir:
        winpython_installer_path = Path(tmpdir) / Path(winpython_installer_url).name
        urlretrieve(winpython_installer_url, winpython_installer_path)

        # Extract the 7z archive to a temp location
        with tempfile.TemporaryDirectory() as extract_temp_dir:
            # Run the 7z.exe to extract the WinPython installer
            subprocess.run(
                [
                    str(s7ip_dir / "7z.exe"),
                    "x",
                    str(winpython_installer_path),
                    f"-o{extract_temp_dir}",
                ]
            )

            # Find the correct directory to extract from, assuming it matches the WPy64*/python*.amd64 pattern
            for root, dirs, files in os.walk(extract_temp_dir):
                if "WPy64" in root and any(
                    "python" in d and "amd64" in d for d in dirs
                ):
                    python_installation_dir = (
                        Path(root)
                        / [d for d in dirs if "python" in d and "amd64" in d][0]
                    )
                    break

            # Copy extracted Python files to `python_dir`
            shutil.copytree(python_installation_dir, python_dir)

        # Create a virtual environment in `python_dir / venv`
        venv_dir = parent_dir / "venv"
        subprocess.run([str(python_dir / "python.exe"), "-m", "venv", str(venv_dir)])

        # Install requirements via pip in the created virtual environment
        requirements_file = (
            parent_dir / "requirements.txt"
        )  # Assuming requirements.txt is in the same folder as the script
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
    tcc_dir = bin_dir / "tcc"

    # Check if TCC is already installed
    try:
        subprocess.check_output(
            [str(tcc_dir / "tcc.exe"), "-h"], stderr=subprocess.STDOUT
        )
        print("TCC already installed, skipping installation.")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
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


# Now you can call install_winpython to do the installation
if __name__ == "__main__":
    install_winpython()
    install_cygwin()
    install_tcc()