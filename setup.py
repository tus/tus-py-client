import sys
import os
from setuptools import setup

import tusclient


if os.environ.get('READTHEDOCS') == 'True':
    install_requires = [
        'requests==2.11.1', 'six==1.10.0', 'tinydb>=3.5.0', 'future==0.16.0'
    ]
else:
    install_requires = [
        'future==0.16.0', 'requests>=2.11.1', 'six==1.10.0',
        'certifi==2017.7.27.1', 'tinydb>=3.5.0'
    ]

PY_VERSION = sys.version_info[0], sys.version_info[1]
if PY_VERSION < (3, 0):
    long_description = open('README.md').read()
else:
    long_description = open('README.md', encoding='utf-8').read()

setup(
    name='tuspy',
    version=tusclient.__version__,
    url='http://github.com/tus/tus-py-client/',
    license='MIT',
    author='Ifedapo Olarewaju',
    install_requires=install_requires,
    author_email='ifedapoolarewaju@gmail.com',
    description='A Python client for the tus resumable upload protocol ->  http://tus.io',
    long_description=(long_description),
    packages=['tusclient', 'tusclient.fingerprint', 'tusclient.storage'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: Communications :: File Sharing',
    ]
)
