from setuptools import setup, find_packages
import pkg_resources
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = f"{ os.path.dirname(lib_folder)}/requirements.txt"
version_path = f"{lib_folder}/version.py"
install_requires = [] 
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

exec(open(version_path).read())

setup(
    name='talos',
    version=__version__, # type: ignore
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'talos = talos:cli_entry',
        ],
    },
)