# NHAIS Adaptor - Developer Notes
The following sections are intended to provide the necessary info on how to configure and run the NHAIS adaptor.

## Pre-requisites

Ensure you have Pipenv installed and on your path, then within nhais directory, run:

`pipenv install`

## Developer setup 

Start IntelliJ

Install Python and EnvFile plugin

Restart IntelliJ

Open nhais component - IntelliJ → File → Open → select nhais folder (../integration-adaptors/nhais)

Open main.py file

You’ll see information that there’s “No Python interpreter configured“

Click “Use Pipenv interpreter“ and wait for indexing to finish

Close project

Open integration-adaptors in IntelliJ (like step 3 but point to root folder of repository)

Select IntelliJ → File → New → Module from existing sources

Point to nhais folder

Select “Create module from existing sources"

Click through wizard and select correct pipenv environment for nhais if it asks for one

Open IntelliJ → File → Project Structure… → select Modules → add root common (all_common) to nhais. 

Now you can add configurations to run each component. Just make sure that each configuration uses correct Python interpreter and set EnvFile:
