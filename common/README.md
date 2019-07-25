# NHS Integration Adaptors Common Utilities

This package contains common utilities used by the various projects that make up the NHS integration adaptors.

## Installation
To use this package as part of your project, ensure you have `pipenv` installed and is on your path, then from your
project's directory run:
```
pipenv install -e ./relative/path/to/package/directory
```
E.g:
```
pipenv install -e ./../common
```

### Run Tests
`pipenv run tests` will run all tests.

### Coverage
`pipenv run unittests-cov` will run all unit tests with coverage enabled. \
`pipenv run coverage-report-xml` will generate an xml file which can then be submitted for coverage analysis. \

### Analysis
To use sonarqube analysis you will need to have installed `sonar-scanner`. \
Ensure sonar-scanner is on your path, and configured for the sonarqube host with appropriate token. \
`sonar-scanner` will use `sonar-project.properties` to submit source to sonarqube for analysis. \
NOTE: Coverage will not show in the analysis unless you have already generated the xml report (as per above.)

