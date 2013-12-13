""" Install
"""
from setuptools import setup, find_packages
import os, sys

PACKAGE_NAME = "ilogin"
PACKAGE_VERSION = "2.0"
SUMMARY = (
    "Single Sign-On script (SSO) that allows you to generate passwords "
    "for each online service you're using. http://iloginr.com"
)
DESCRIPTION = (
    open("README.rst", 'r').read() + '\n\n' +
    open('HISTORY.rst', 'r').read()
)

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=SUMMARY,
      long_description=DESCRIPTION,
      author='Alin Voinea',
      author_email='alin.voinea@gmail.com',
      url='http://github.com/avoinea/ilogin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      entry_points = {
          'console_scripts': [
              'ilogin_old = ilogin.ilogin:main',
              'ilogin = ilogin.iloginr:main'
          ]},
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          "Programming Language :: Python",
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
