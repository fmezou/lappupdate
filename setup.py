from setuptools import setup, find_packages
# from distutils.core import setup
# from version import *
import glob

setup(
    name="lapptrack",
    version="0.1.0-dev.0",
    description="Tracks and downloads application installers or its update.",
    long_description="Lightweight application update (commonly known as "
                     "lAppUpdate) is a set of scripts to download and deploy "
                     "application on a small network of computers or "
                     "standalone computers running under Microsoft Windows.",
    url="https://github.com/fmezou/lappupdate",
    license="GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007",
    author="Frederic MEZOU",
    author_email="frederic.mezou@example.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Intended Audience :: System Administrators",
        "Topic :: System :: Software Distribution",

        # Pick your license as you wish (should match "license" above)
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.5",
    ],
    keywords="Distribution Software Administrator",
    packages=find_packages(exclude=["tests"]),
    install_requires=["", 'lxml'],
    package_data={
        "lapptrack": ["*.example.ini", "*.tmpl.html"],
        "lapptrack.cots": ["padspec40.xml"]
    },
    data_files=[
        ("man", glob.glob("_build/html/**/*.*", recursive=True))
    ],
    entry_points={
         "console_scripts": [
             "lapptrack=lapptrack.lapptrack:main",
         ],
     },
)
