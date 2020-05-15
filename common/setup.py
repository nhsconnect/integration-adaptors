from distutils.core import setup

import setuptools

setup(
    name='integration-adaptors-common',
    version='',
    packages=setuptools.find_packages(),
    url='',
    license='',
    author='Gareth Allan',
    author_email='',
    description='Common utilities used by the NHS integration adaptors projects.',
    install_requires=[
        'pystache~=0.5',
        'lxml~=4.4',
        'python-qpid-proton~=0.28',
        'tornado~=6.0',
        'isodate~=0.6',
        'motor~=2.1'
    ]
)
