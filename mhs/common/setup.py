from distutils.core import setup

import setuptools

setup(
    name='mhs-common',
    version='',
    packages=setuptools.find_packages(),
    url='',
    license='',
    author='',
    author_email='',
    description='Common utilities used by the NHS integration adaptors projects.',
    install_requires=[
        'defusedxml~=0.6',
        'aioboto3~=8.0',
        'tornado~=6.0',
        'isodate~=0.6'
    ]
)
