"""setuptools entry point: package metadata and install-time KEGG_decoder fetch."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests
from setuptools import find_packages, setup
from setuptools.command.install import install

VERSION_FILE = "kegganog/version.py"
SCRIPT_URL = (
    "https://raw.githubusercontent.com/bjtully/BioData/master/KEGGDecoder/KEGG_decoder.py"
)
SCRIPT_RELATIVE_PATH = Path("kegganog") / "processing" / "KEGG_decoder.py"
REQUEST_TIMEOUT_SECONDS = 10


def load_version(namespace_file: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    with open(namespace_file, encoding="utf-8") as handle:
        exec(handle.read(), namespace)
    return namespace


def download_external_script(install_lib: str) -> None:
    """
    Download KEGG_decoder.py into the installed package (same behavior as before).

    On network or HTTP failure: print an error message and return without raising,
    so installation still completes (runtime may fail later if the script is missing).
    """
    target_path = Path(install_lib) / SCRIPT_RELATIVE_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading KEGG-Decoder script from:\n  {SCRIPT_URL}\n  -> {target_path}")
    try:
        response = requests.get(SCRIPT_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        target_path.write_bytes(response.content)
        print(
            f"Successfully downloaded KEGG_decoder.py "
            f"({target_path.stat().st_size} bytes) to {target_path}"
        )
    except requests.RequestException as exc:
        print(f"Failed to download {SCRIPT_URL}: {exc}")


class CustomInstallCommand(install):
    """Custom installation to download KEGG_decoder.py."""

    def run(self) -> None:
        install.run(self)
        download_external_script(self.install_lib)


version = load_version(VERSION_FILE)

setup(
    name="kegganog",
    version=version["__version__"],
    description="A tool for generating KEGG heatmaps from eggNOG-mapper outputs.",
    long_description=Path("README_PyPI.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Ilia Popov",
    author_email="iljapopov17@gmail.com",
    url="https://github.com/iliapopov17/KEGGaNOG",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "kegganog": ["static/**/*"],
    },
    cmdclass={"install": CustomInstallCommand},
    entry_points={
        "console_scripts": [
            "KEGGaNOG=kegganog.kegganog:main",
            "kegganog=kegganog.kegganog:main",
        ],
    },
    install_requires=Path("requirements.txt").read_text(encoding="utf-8").splitlines(),
    python_requires=">=3.10,<=3.16",
)
