from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import requests

VERSION_FILE = "kegganog/version.py"


class CustomInstallCommand(install):
    """Custom installation to download KEGG_decoder.py."""

    def run(self):
        # Run standard installation
        install.run(self)

        # Define where to download the script
        install_dir = os.path.join(self.install_lib, "kegganog")  # Adjust if needed
        os.makedirs(install_dir, exist_ok=True)  # Ensure the directory exists

        # Define the script URL and target path
        script_url = "https://raw.githubusercontent.com/bjtully/BioData/master/KEGGDecoder/KEGG_decoder.py"
        script_path = os.path.join(install_dir, "processing/KEGG_decoder.py")

        # Download the script
        print(f"Downloading {script_url} to {script_path}...")
        try:
            response = requests.get(script_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            with open(script_path, "wb") as f:
                f.write(response.content)
            print(f"Successfully downloaded {script_path}")
        except requests.RequestException as e:
            print(f"Failed to download {script_url}: {e}")


version = {}
with open(VERSION_FILE) as f:
    exec(f.read(), version)

setup(
    name="kegganog",
    version=version["__version__"],
    description="A tool for generating KEGG heatmaps from eggNOG-mapper outputs.",
    long_description=open("README_PyPI.md").read(),
    long_description_content_type="text/markdown",
    author="Ilia Popov",
    author_email="iljapopov17@gmail.com",
    url="https://github.com/iliapopov17/KEGGaNOG",
    packages=find_packages(),
    cmdclass={"install": CustomInstallCommand},
    entry_points={
        "console_scripts": [
            "KEGGaNOG=kegganog.kegganog:main",  # Maps the command to the main function
        ],
    },
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.9,<=3.16",
)
