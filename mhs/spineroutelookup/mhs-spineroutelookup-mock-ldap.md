## MHS Spine Route Lookup component - Mock LDAP

Spine Route Lookup component has a built in LDAP mocking capability
To be able to use it, three json configuration files has to be present:

- server_info.json
- server_schema.json
- server_entries.json

# Downloading real LDAP configuration

Although LDAP configuration is already available on NHSD S3 bucket `nhsd-integration-adaptors` in
`mock_ldap_data` folder, you can still easily download new configuration from real OpenTest LDAP server. 
To do so, navigate to: 

`mhs/spineroutelookup/lookup` 

launch 

`pipenv shell`

run 

`python sds_mock_connection_factory.py <output_path>`

where

`<output_path>` is the path on your computer where 3 json files will be downloaded to

# Running Spine Route Lookup with built-in Mock LDAP

To enable LDAP mock, environment variable `MHS_LDAP_MOCK_DATA_URL` have to be set to one of supported values (more information below)

Running Spine Route Lookup with mock LDAP enabled, will download 3 config files from given location 
to local `mhs/spineroutelookup/mock_ldap_data` folder (ignored in git) and use the data to feed the mock LDAP 

There is another optional variable `MHS_FAKE_SPINE_URL` which value is used to replace LDAP configuration to point to the desired Spine server instead of real one.
For example:

`MHS_FAKE_SPINE_URL: "http://fake-spine/"`

Currently there are 2 options of providing configuration files:

1. From local file system

Set env var `MHS_LDAP_MOCK_DATA_URL: "file://tmp/mock_ldap_data"` pointing to your local file system folder location of 3 config files

2. From S3

Set env var `MHS_LDAP_MOCK_DATA_URL: "s3://nhsd-integration-adaptors/mock_ldap_data"` pointing to S3 folder location of 3 config files.
By default `boto3` will use standard credentials lookup flow (https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html).
If you want to provide non-default credentials profile, set the `MHS_AWS_PROFILE: <profile_name>` env variable