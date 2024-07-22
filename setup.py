from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in elaguiely/__init__.py
from elaguiely import __version__ as version

setup(
	name="elaguiely",
	version=version,
	description="elaguiely",
	author="elaguiely",
	author_email="elaguiely",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
