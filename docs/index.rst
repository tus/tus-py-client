.. tusclient documentation master file, created by
   sphinx-quickstart on Mon Oct 10 15:11:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tusclient's documentation!
=====================================

|Build Status|

.. |Build Status| image:: https://travis-ci.org/ifedapoolarewaju/tus-py-client.svg?branch=master
   :target: https://travis-ci.org/ifedapoolarewaju/tus-py-client

# tus-py-client
A Python client for the tus resumable upload protocol ->  http://tus.io

Contents:

.. toctree::
   :maxdepth: 4

   tusclient


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Quickstart
==========

Installation
~~~~~~~~~~~~

.. code:: bash

    pip install tuspyclient

Now you are ready to use the api.

.. code:: python

    from tusclient import client

    # Set Authorization headers if it is required
    # by the tus server.
    my_client = client.TusClient('http://master.tus.io/files/',
                                  headers={'Authorization': 'Basic xxyyZZAAbbCC='})

    # set more headers
    my_client.set_headers({'HEADER_NAME': 'HEADER_VALUE'})

    uploader = my_client.uploader('path/to/file.ext', chunk_size=200)

    # upload a chunk i.e 200 bytes
    uploader.upload_chunk()

    # uploads the entire file.
    # This uploads chunk by chunk.
    uploader.upload()

    # you could increase the chunk size to reduce the
    # number of upload_chunk cycles.
    uploader.chunk_size = 800
    uploader.upload()

    # Continue uploading chunks till total chunks uploaded reaches 1000 bytes.
    uploader.upload(stop_at=1000)

If the upload url is known and the client headers are not required,
uploaders can also be used standalone.

.. code:: python

    from tusclient.uploader import Uploader

    my_uploader = Uploader('path/to/file.ext',
                            url='http://master.tus.io/files/abcdef123456',
                            chunk_size=200)
