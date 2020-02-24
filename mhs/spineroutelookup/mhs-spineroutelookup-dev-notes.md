

## MHS Spine Route Lookup component - Developer Notes

The following sections are intended to provide the necessary info on how to set up workstation to start development. As of now it was tested/used on Mac (OS X).

### Pre-requisites

You'll need to have a connection to Spine. For testing purposes, you can use [Opentest](https://nhs-digital-opentest.github.io/Welcome/index.html). 
See [Setup an OpenTest connection](../../setup-opentest.md) for details.

Install [PyCharm](https://www.jetbrains.com/pycharm/) and add [EnvFile](https://plugins.jetbrains.com/plugin/7861-envfile) plugin to it (it is used to supply environment variables to python executable).

Finally, ensure you have [Pipenv](https://github.com/pypa/pipenv) installed  
```
brew install pipenv
```
and available on your `$PATH`

### Set up

Within root directory of spineroutelookup (`integration-adaptors/mhs/spineroutelookup`) project run:
```
pipenv install --dev
```
Then add common libraries using:
```
pipenv install -e ./../common
```
After installing/configuring dependencies with pipenv, open PyCharm project using path: 
```
/_path_to_repository/integration-adaptors/mhs/spineroutelookup/
```
Make sure project interpreter is configured as Pipenv (Preferences -> Project -> Project interpreter)

Make a copy of `nhs-spineroutelookup-env-example.yaml` as `nhs-spineroutelookup-env.yaml` (this file has already been added to .gitignore) and fill it with data (mostly certificates - be vary of indentation for them) obtained earlier for OpenTest access

Last step is to add new Python Run Configuration:
1. Point script path to `main.py`
2. Switch to EnvFile tab
3. Enable EnvFile plugin and add yaml file you edited and saved earlier.
4. Make sure your connection to OpenTest is active
4. Project is ready to run!