#!/usr/bin/env python3
"""Fix ruamel namespace package installation issue.

This script ensures that the ruamel namespace package is properly set up
in the current virtual environment.
"""

import importlib.util
import site
import subprocess
import sys
from pathlib import Path


def get_site_packages() -> Path | None:
    """Get the site-packages directory for the current environment."""
    # Get all site-packages directories
    site_packages = site.getsitepackages()

    # Find the one in the virtual environment
    for sp in site_packages:
        if ".venv" in sp or "venv" in sp:
            return Path(sp)

    # Fallback to the first one
    return Path(site_packages[0]) if site_packages else None


def create_namespace_init(ruamel_dir: Path) -> None:
    """Create the namespace __init__.py file."""
    init_file = ruamel_dir / "__init__.py"
    if not init_file.exists():
        print(f"Creating namespace __init__.py: {init_file}")
        init_file.write_text("__import__('pkg_resources').declare_namespace(__name__)\n")


def reinstall_ruamel_yaml() -> None:
    """Reinstall ruamel.yaml package."""
    print("Reinstalling ruamel.yaml...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-deps", "ruamel.yaml"],
        capture_output=True,
        check=False,
    )


def setup_yaml_directory(site_packages_dir: Path, yaml_dir: Path) -> None:
    """Set up the yaml directory if it doesn't exist."""
    # Look for the installed files
    dist_info_pattern = "ruamel.yaml-*.dist-info"
    dist_infos = list(site_packages_dir.glob(dist_info_pattern))

    if dist_infos:
        print(f"Found dist-info: {dist_infos[0]}")
        # Create yaml directory
        yaml_dir.mkdir(parents=True, exist_ok=True)

        # Look for ruamel yaml files in RECORD
        record_file = dist_infos[0] / "RECORD"
        if record_file.exists():
            for line in record_file.read_text().splitlines():
                if line.startswith("ruamel/yaml/"):
                    file_path = line.split(",")[0]
                    src = site_packages_dir / file_path
                    dst = site_packages_dir / file_path

                    # Ensure directory exists
                    dst.parent.mkdir(parents=True, exist_ok=True)

                    print(f"Checking: {src}")


def fix_ruamel_namespace() -> bool:
    """Fix the ruamel namespace package issue."""
    site_packages_dir = get_site_packages()
    if not site_packages_dir:
        print("Error: Could not find site-packages directory")
        return False

    print(f"Site-packages directory: {site_packages_dir}")

    # Create ruamel directory if it doesn't exist
    ruamel_dir = site_packages_dir / "ruamel"
    if not ruamel_dir.exists():
        print(f"Creating ruamel namespace directory: {ruamel_dir}")
        ruamel_dir.mkdir(parents=True)

    # Create __init__.py for namespace package
    create_namespace_init(ruamel_dir)

    # Check if yaml directory exists
    yaml_dir = ruamel_dir / "yaml"

    # If yaml directory doesn't exist, we need to extract the package files
    if not yaml_dir.exists():
        print("yaml subdirectory not found, attempting to extract package files...")

        # Try to reinstall the package properly
        reinstall_ruamel_yaml()

        # Check again and set up if needed
        if not yaml_dir.exists():
            setup_yaml_directory(site_packages_dir, yaml_dir)

    # Verify the fix
    if importlib.util.find_spec("ruamel.yaml") is not None:
        print("✅ Successfully fixed ruamel namespace package!")
        return True
    print("❌ Failed to fix ruamel namespace package")
    return False


if __name__ == "__main__":
    if fix_ruamel_namespace():
        sys.exit(0)
    else:
        sys.exit(1)
