from setuptools import setup

import tusclient


setup(
    name='tusclient',
    version=tusclient.__version__,
    url='http://github.com/ifedapoolarewaju/tus-py-client/',
    license='MIT',
    author='Ifedapo Olarewaju',
    install_requires=['pycurl==7.43.0',
                      'requests==2.11.1',
                      'six==1.10.0',
                      ],
    author_email='ifedapoolarewaju@gmail.com',
    description='A Python client for the tus resumable upload protocol',
    packages=['tusclient'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Upload',
    ]
)
