# NHAIS Adaptor - Developer Notes
The following sections are intended to provide the necessary info on how to configure and run the NHAIS adaptor.

Environment Variables are used throughout application, an example can be found in `nhais-env-example.yaml`. 

## Pre-requisites

Ensure you have Pipenv installed and on your path, then within NHAIS directory, run:

`pipenv install`

## Developer setup 

Open integration-adaptors in IDE (but point to root folder of repository)

File → Project Structure → SDK → Add new Python SDK → Select Pipenv Environment and provide a path to the executable of my pipenv.

Select File → New → Module from existing sources

Point to NHAIS folder

Select “Create module from existing sources"

Click through wizard and select correct pipenv environment for NHAIS if it asks for one

Open File → Project Structure… → select Modules → add root common (all_common) to NHAIS. 

Now you can add configurations to run component. Just make sure that each configuration uses correct Python interpreter and set EnvFile:
