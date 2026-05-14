from setuptools import setup, find_packages

setup(
    name="unidesk",
    version="1.0",
    description="Helper app for UniOS written in python/Qt",
    long_description="University of Western Macedonia Student Welcomer",
    author="OpenSource UoM",
    author_email="opensource@uom.edu.gr",
    # Crucial for the new structure:
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["PyQt6"],
    entry_points={
        'console_scripts': [
            'unidesk = unidesk.main:main',
        ],
    },
)