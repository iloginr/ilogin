""" Install
"""

from setuptools import setup, find_packages

PACKAGE_NAME = "ilogin"
PACKAGE_VERSION = "4.0"
SUMMARY = (
    "Single Sign-On script (SSO) that allows you to generate unique passwords "
    "for each online and offline service you're using."
)

with open("README.rst", "r", encoding="utf-8") as rfile:
    with open("HISTORY.rst", "r", encoding="utf-8") as hfile:
        DESCRIPTION = f"{rfile.read()}\n\n{hfile.read()}"

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=SUMMARY,
    long_description=DESCRIPTION,
    author="Alin Voinea",
    author_email="alin.voinea@gmail.com",
    url="http://github.com/avoinea/ilogin",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    entry_points={
        "console_scripts": [
            "ilogin1 = ilogin.ilogin:main",
            "ilogin2 = ilogin.ilogin2:main",
            "ilogin3 = ilogin.ilogin3:main",
            "ilogin = ilogin.ilogin3:main",
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
