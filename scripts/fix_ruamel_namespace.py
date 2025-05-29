#!/usr/bin/env python3
"""
Fix ruamel namespace package installation issue.

This script ensures that the ruamel namespace package is properly set up
in the current virtual environment.
"""
import os
import sys
import site
import subprocess


def get_site_packages():
    """Get the site-packages directory for the current environment."""
    # Get all site-packages directories
    site_packages = site.getsitepackages()

    # Find the one in the virtual environment
    for sp in site_packages:
        if '.venv' in sp or 'venv' in sp:
            return sp

    # Fallback to the first one
    return site_packages[0] if site_packages else None


def fix_ruamel_namespace():
    """Fix the ruamel namespace package issue."""
    site_packages_dir = get_site_packages()
    if not site_packages_dir:
        print("Error: Could not find site-packages directory")
        return False

    print(f"Site-packages directory: {site_packages_dir}")

    # Create ruamel directory if it doesn't exist
    ruamel_dir = os.path.join(site_packages_dir, 'ruamel')
    if not os.path.exists(ruamel_dir):
        print(f"Creating ruamel namespace directory: {ruamel_dir}")
        os.makedirs(ruamel_dir)

    # Create __init__.py for namespace package
    init_file = os.path.join(ruamel_dir, '__init__.py')
    if not os.path.exists(init_file):
        print(f"Creating namespace __init__.py: {init_file}")
        with open(init_file, 'w') as f:
            f.write("__import__('pkg_resources').declare_namespace(__name__)\n")

    # Check if yaml directory exists
    yaml_dir = os.path.join(ruamel_dir, 'yaml')

    # If yaml directory doesn't exist, we need to extract the package files
    if not os.path.exists(yaml_dir):
        print("yaml subdirectory not found, attempting to extract package files...")

        # Try to reinstall the package properly
        print("Reinstalling ruamel.yaml...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-deps', 'ruamel.yaml'],
                      capture_output=True)

        # Check again
        if not os.path.exists(yaml_dir):
            # Look for the installed files
            dist_info_pattern = 'ruamel.yaml-*.dist-info'
            import glob
            dist_infos = glob.glob(os.path.join(site_packages_dir, dist_info_pattern))

            if dist_infos:
                print(f"Found dist-info: {dist_infos[0]}")
                # The files might be installed flat, we need to move them
                # This is a last resort
                yaml_files = glob.glob(os.path.join(site_packages_dir, '*.py'))
                yaml_files.extend(glob.glob(os.path.join(site_packages_dir, '*.pyx')))
                yaml_files.extend(glob.glob(os.path.join(site_packages_dir, '*.so')))

                # Create yaml directory
                os.makedirs(yaml_dir, exist_ok=True)

                # Look for ruamel yaml files in RECORD
                record_file = os.path.join(dist_infos[0], 'RECORD')
                if os.path.exists(record_file):
                    with open(record_file) as f:
                        for line in f:
                            if line.startswith('ruamel/yaml/'):
                                file_path = line.split(',')[0]
                                src = os.path.join(site_packages_dir, file_path)
                                dst = os.path.join(site_packages_dir, file_path)

                                # Ensure directory exists
                                os.makedirs(os.path.dirname(dst), exist_ok=True)

                                print(f"Checking: {src}")

    # Verify the fix
    try:
        import ruamel.yaml
        print("✅ Successfully fixed ruamel namespace package!")
        return True
    except ImportError as e:
        print(f"❌ Failed to fix ruamel namespace package: {e}")
        return False


if __name__ == '__main__':
    if fix_ruamel_namespace():
        sys.exit(0)
    else:
        sys.exit(1)
