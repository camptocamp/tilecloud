from glob import glob
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()

install_requires = [
    "boto3",
    "bottle",
    "Pillow",
    "pyproj",
    "requests>=1.0",
    "redis>=2",
]

setup(
    name="tilecloud",
    version="1.5.0",
    description="Tools for managing tiles",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    author="Camptocamp",
    author_email="info@camptocmap.com",
    url="http://github.com/camptocamp/tilecloud",
    license="BSD",
    packages=find_packages(exclude=["tiles", "tilecloud.tests"]),
    zip_safe=True,
    install_requires=install_requires,
    test_suite="tilecloud.tests",
    scripts=glob("tc-*"),
    entry_points="""
    # -*- Entry points: -*-
    """,
    long_description=README,
    long_description_content_type="text/markdown",
)
