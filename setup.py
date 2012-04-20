from setuptools import setup, find_packages
from glob import glob
import os

version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

install_requires = [
        'bottle',
        'pyproj',
        ]

setup_requires = [
        'nose',
        ]

tests_require = install_requires + [
        'coverage',
        ]

setup(
        name='tilecloud',
        version=version,
        description='Tools for managing tiles',
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
        ],
        author='Tom Payne',
        author_email='twpayne@gmail.com',
        url='http://github.com/twpayne/tilecloud',
        license='BSD',
        packages=find_packages(exclude=['tiles', 'tilecloud.tests']),
        zip_safe=True,
        install_requires=install_requires,
        setup_requires=setup_requires,
        tests_require=tests_require,
        test_suite='tilecloud.tests',
        scripts=glob('tc-*'),
        entry_points="""
        # -*- Entry points: -*-
        """,
        long_description=README,
        )
