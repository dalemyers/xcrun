#!/usr/bin/env python3

from os import path

from setuptools import setup, find_packages


def run_setup():
    """Run package setup."""
    here = path.abspath(path.dirname(__file__))

    # Get the long description from the README file
    try:
        with open(path.join(here, 'README.md')) as f:
            long_description = f.read()
    except:
        # This happens when running tests
        long_description = None

    setup(
        name='xcrun',
        version='0.3',
        description='Python wrapper around the xcrun utility',
        long_description=long_description,
        url='https://github.com/dalemyers/xcrun',
        author='Dale Myers',
        author_email='dale@myers.io',
        license='MIT',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: MacOS X',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities'
        ],

        keywords='xcode xcrun simctl ios simulator',
        packages=find_packages(exclude=['docs', 'tests'])
    )

if __name__ == "__main__":
    run_setup()