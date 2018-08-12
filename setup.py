import sys
import os
from setuptools import setup

import tusclient


install_requires = [
    'future>=0.16.0', 'requests>=2.18.4', 'six>=1.11.0', 'tinydb>=3.5.0'
]
if os.environ.get('READTHEDOCS') != 'True':
    install_requires.append('certifi>=2018.1.18')
tests_require = ['responses>=0.5.1', 'mock>=2.0.0', 'coverage>=4.2', 'pytest>=3.0.3',
'pytest-cov>=2.3.1']

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
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': ['tox>=2.3.1', 'sphinx-autobuild==0.7.1', 'Sphinx==1.7.1']
    },
    author_email='ifedapoolarewaju@gmail.com',
    description=
    'A Python client for the tus resumable upload protocol ->  http://tus.io',
    long_description=(long_description),
    long_description_content_type='text/markdown',
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
    ])
