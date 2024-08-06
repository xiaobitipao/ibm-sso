import os
import shutil
import subprocess
import sys


def copy_sitecustomize():
    # Get the path to the virtual environment
    venv_path = subprocess.check_output(
        ['pipenv', '--venv'],
        universal_newlines=True
    ).strip()

    # Get the path to the site-packages directory in the virtual environment
    python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
    site_packages_path = os.path.join(
        venv_path, 'lib', python_version, 'site-packages')

    # Specify the path to sitecustomize.py
    sitecustomize_dir = os.path.dirname(os.path.abspath(__file__))
    sitecustomize_src = os.path.join(sitecustomize_dir, 'sitecustomize.py')
    sitecustomize_dst = os.path.join(site_packages_path, 'sitecustomize.py')

    # Copy sitecustomize.py
    shutil.copyfile(sitecustomize_src, sitecustomize_dst)
    print(f'sitecustomize.py has been copied to {sitecustomize_dst}')


if __name__ == '__main__':
    copy_sitecustomize()
