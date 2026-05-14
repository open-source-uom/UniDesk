from setuptools import setup, find_packages

setup(
    name="unidesk",
    version="1.0",
    description="Helper app for UniOS written in python/Qt ",
    long_description="Helper app for UniOS written in python/Qt",
    author="OpenSource UoM",
    author_email="opensource@uom.edu.gr",
    packages=find_packages(),
    install_requires=["PyQt6"],
    entry_points={
        'console_scripts': [
            'unidesk = src.main:main',
        ],
    },
)