import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "myownci_pysupport",
    version = "0.0.1",
    author = "Patrick Atamaniuk",
    author_email = "patrick.atamaniuk@wibas.de",
    description = ("Utility classes for myownci metal and worker"),
    license = "BSD",
    keywords = "continuous integration support",
    url = "http://packages.python.org/myownci_pysupport",
    packages=['myownci'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
