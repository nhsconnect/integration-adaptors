from distutils.core import setup

import setuptools

setup(
    name='mhs_common',
    version='',
    packages=setuptools.find_packages(),
    url='',
    license='',
    author='',
    author_email='',
    description='Common utilities used by the NHS integration adaptors projects.',
    install_requires=[
        'defusedxml',
        'aioboto3'
    ]
)
