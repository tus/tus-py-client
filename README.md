# tus-py-client [![Build Status](https://github.com/tus/tus-py-client/actions/workflows/CI.yml/badge.svg)](https://github.com/tus/tus-py-client/actions/workflows/CI.yml)

> **tus** is a protocol based on HTTP for _resumable file uploads_. Resumable
> means that an upload can be interrupted at any moment and can be resumed without
> re-uploading the previous data again. An interruption may happen willingly, if
> the user wants to pause, or by accident in case of a network issue or server
> outage.

**tus-py-client** is a Python client for uploading files using the _tus_ protocol to any remote server supporting it.

## Documentation

See documentation here: http://tus-py-client.readthedocs.io/en/latest/

## Get started

```bash
pip install tuspy
```

Now you are ready to use the api.

```python
from tusclient import client

# Set Authorization headers if it is required
# by the tus server.
my_client = client.TusClient('http://tusd.tusdemo.net/files/',
                              headers={'Authorization': 'Basic xxyyZZAAbbCC='})

# Set more headers.
my_client.set_headers({'HEADER_NAME': 'HEADER_VALUE'})

uploader = my_client.uploader('path/to/file.ext', chunk_size=200)

# A file stream may also be passed in place of a file path.
fs = open('path/to/file.ext', mode=)
uploader = my_client.uploader(file_stream=fs, chunk_size=200)

# Upload a chunk i.e 200 bytes.
uploader.upload_chunk()

# Uploads the entire file.
# This uploads chunk by chunk.
uploader.upload()

# you could increase the chunk size to reduce the
# number of upload_chunk cycles.
uploader.chunk_size = 800
uploader.upload()

# Continue uploading chunks till total chunks uploaded reaches 1000 bytes.
uploader.upload(stop_at=1000)
```

If the upload url is known and the client headers are not required, uploaders can also be used standalone.

```python
from tusclient.uploader import Uploader

my_uploader = Uploader('path/to/file.ext',
                       url='http://tusd.tusdemo.net/files/abcdef123456',
                       chunk_size=200)
```

## Development

If you want to work on tus-py-client internally, follow these few steps:

1. Setup virtual environment and install dependencies

   ```bash
   python -m venv env/
   source env/bin/activate
   pip install -e .[test]
   ```

2. Running tests

   ```bash
   pytest
   ```

3. Releasing a new version (see https://realpython.com/pypi-publish-python-package/)

   ```bash
   # Update version in tusclient/__init__.py
   vim tusclient/__init__.py

   # Update changelogs
   vim CHANGELOG.md

   pytest

   # Commit and tag
   git commit -m 'v1.2.3'
   git tag v1.2.3

   # Build and release
   pip install build twine
   python -m build
   twine check dist/*
   twine upload dist/*

   # Then: make release on GitHub
   ```

## License

MIT
