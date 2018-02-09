from setuptools import setup, find_packages
from glob import glob
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

install_requires = [
    'boto3',
    'bottle',
    'Pillow',
    'pyproj',
    'requests>=1.0',
    'six',
]

setup(
    name='tilecloud',
    version='0.5.0.dev7',
    description='Tools for managing tiles',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    author='Tom Payne',
    author_email='twpayne@gmail.com',
    url='http://github.com/camptocamp/tilecloud',
    license='BSD',
    packages=find_packages(exclude=['tiles', 'tilecloud.tests']),
    zip_safe=True,
    install_requires=install_requires,
    test_suite='tilecloud.tests',
    scripts=glob('tc-*'),
    entry_points="""
    # -*- Entry points: -*-
    """,
    long_description=README,
)
