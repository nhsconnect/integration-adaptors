

## MHS Inbound component - Developer Notes

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

Within root directory of inbound (`integration-adaptors/mhs/inbound`) project run:
```
pipenv install --dev
```
Then add common libraries using:
```
pipenv install -e ./../common
```
After installing/configuring dependencies with pipenv, open PyCharm project using path: 
```
/_path_to_repository/integration-adaptors/mhs/inbound/
```
Make sure project interpreter is configured as Pipenv (Preferences -> Project -> Project interpreter)

### Dependencies set up

The following command will bring up dynamodb and rabbitmq:
```
docker-compose -f  docker-compose-inbound.yml up
```

### Starting the inbound component locally

To configure the environment variables, run:
```
source stub-config.sh
```
Launch the python environment with dependencies:
```
pipenv shell
```
To start the inbound server, run:
```
python main.py
```

