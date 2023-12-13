### 1.0.3 / 2023-12-13

- Add explicit test fixtures to fix tests on Windows by @nhairs in https://github.com/tus/tus-py-client/pull/91
- Remove unneeded `six` dependency (was used for Python 2) by @a-detiste in https://github.com/tus/tus-py-client/pull/90
- Fix calls to `upload_chunk` by @Acconut in https://github.com/tus/tus-py-client/pull/92

### 1.0.2 / 2023-11-30

- Remove unnecessary future install requirement [#81](https://github.com/tus/tus-py-client/pulls/81)
- Expose typing information (PEP 561) [#87](https://github.com/tus/tus-py-client/issues/87)

### 1.0.1 / 2023-06-20

- Fix bug preventing `verify_tls_cert` from being applied to `HEAD` requests (https://github.com/tus/tus-py-client/pull/80)
- Fix bug preventing empty files from being uploaded (https://github.com/tus/tus-py-client/pull/78)

### 1.0.0 / 2022-06-17

- Drop support for Python 2 (https://github.com/tus/tus-py-client/pull/35)
- Add support for asyncIO using AsyncUploader class (https://github.com/tus/tus-py-client/pull/35)
- Use only first block of the file for a finger print (https://github.com/tus/tus-py-client/pull/37)
- Allow all 2XX status code for an upload response (https://github.com/tus/tus-py-client/pull/44)

### 0.2.5 / 2020-06-5

### 0.2.4/ 2019-14-01

- Add support for tus upload-checksum header

### 0.2.3/ 2018-13-03

- Refine connection error handling
- Make long description render correctly on pypi.org
- Set default chunksize to largest possible number

### 0.2.2/ 2018-19-03

- Replace the use of PyCurl with builtin http.client
- Remove unwanted debug printing

### 0.2.1 / 2017-12-02

- Fix installtion and Doc autogeneration issue

### 0.2 / 2017-12-02

- Support for URL storage
- Use uploader without Client [#14](https://github.com/tus/tus-py-client/issues/14)

### 0.1.3 / 2017-11-15

- Fix installation issues, due to missing readme.

### 0.1.2 / 2017-10-27

- Fix PyCurl ssl error [#11](https://github.com/tus/tus-py-client/issues/11)

### 0.1.1 / 2017-10-12

- Support relative upload urls (Thank you @ciklop)
- Unpin requests library version (Thank you @peixian)
- Test against Python 3.6 (Thank you @thedrow)

### 0.1 / 2017-07-10

- Automatically retry a chunk upload on failure.
- Read tus server response content `uploader.request.response_content`.
- More http request details in Tus Exception.

### 0.1a2 / 2016-10-31

- Allow upload-metadata
- Upload files from file stream
- Better request error handling
- Cleaner retrieval of offset after chunk upload

### 0.1a1 / 2016-10-13

- Alpha release
