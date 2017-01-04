from setuptools import setup
from setuptools import find_packages

setup(
    name="restrictionschangingapp",
    description="A web app for changing the restrictions for a particular object in the ldr",
    long_description="a test",
    version="0.0.1dev",
    author="Tyler Danstrom",
    author_email="tdanstrom@uchicago.edu",
    packages=find_packages(
        exclude=[
            "build",
            "bin",
            "dist",
            "tests",
            "restrictionschangingapp.egg-info"
        ]
    ),
    install_requires=[
        'flask',
        'pypremis'
    ]
)
