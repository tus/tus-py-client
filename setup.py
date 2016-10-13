import os
from setuptools import setup

import tusclient


on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    install_requires = ['requests==2.11.1', 'six==1.10.0', ]
else:
    install_requires = ['pycurl==7.43.0', 'requests==2.11.1', 'six==1.10.0']


setup(
    name='tuspy',
    version=tusclient.__version__,
    url='http://github.com/ifedapoolarewaju/tus-py-client/',
    license='MIT',
    author='Ifedapo Olarewaju',
    install_requires=install_requires,
    author_email='ifedapoolarewaju@gmail.com',
    description='A Python client for the tus resumable upload protocol ->  http://tus.io',
    packages=['tusclient'],
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
