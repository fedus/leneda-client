from setuptools import setup, find_packages
import os
import re

# Get the absolute path to the directory containing setup.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read version from version.py without importing
version_file = os.path.join(BASE_DIR, "src", "leneda", "version.py")
with open(version_file, encoding="utf-8") as f:
    version_content = f.read()

# Extract version with regex
version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', version_content)
if not version_match:
    raise RuntimeError(f"Unable to find version string in {version_file}")
VERSION = version_match.group(1)

# Read the contents of README.md
with open(os.path.join(BASE_DIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with open(os.path.join(BASE_DIR, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="leneda-client",
    version=VERSION,
    description="Python client for the Leneda energy data platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="fedus",
    author_email="fedus@dillendapp.eu",
    url="https://github.com/fedus/leneda-client",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={"leneda": ["py.typed"]},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords="leneda, energy, api, client",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/leneda-client/issues",
        "Source": "https://github.com/yourusername/leneda-client",
        "Documentation": "https://github.com/yourusername/leneda-client#readme",
    },
)