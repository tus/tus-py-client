[![Build Status](https://travis-ci.org/ifedapoolarewaju/tus-py-client.svg?branch=master)](https://travis-ci.org/ifedapoolarewaju/tus-py-client)

# tus-py-client
A Python client for the tus resumable upload protocol

## Get started
clone the repo

```bash
git clone https://github.com/ifedapoolarewaju/tus-py-client
```

Navigate to the tus client directory then run the following command to install it's dependencies

```bash
pip install -r requirements.txt
```

Now you are ready to use the api

```python
from tusclient import endpoint
from tusclient import upload

end_point = endpoint.EndPoint('http://master.tus.io/files/')

# chunk_size is optional
uploader = upload.FileUpload('YOUR/FILE/PATH.EXTENSION', end_point=end_point, chunk_size=2048)

# you may also specify a url and ignore the end_point parameter
uploader = upload('YOUR/FILE/PATH.EXTENSION', url='http://master.tus.io/files/4467e4675abc75edff442', chunk_size=2048)

# upload a chunk i.e 2048 bytes
uploader.upload_chunk()

# upload entire file
uploader.upload()
```
