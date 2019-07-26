# Supplier Example

An example web application that uses the assets from the SCR package to
generate a GP Summary Update request and send it to an instance of the MHS reference implementation. This application is intended to show
how the national integration adaptors can be used together to simplify integration.

The example consists of a simple [Flask](https://www.fullstackpython.com/flask.html) application, which presents a web
page containing a form that can be submitted in order to build a GP Summary Update request and send it to an MHS
implementation listening on the local machine.

## Running the Example

### Setting up your Environment
To setup your environment, ensure you have `pipenv` installed and on your path, then from this project's directory run:
```
pipenv install
```

### Running the Example Application
Once you have set up your environment (as above), you can run the supplier example with the following Pipenv command:
```
pipenv run server
```
This will start a webserver and print the URL that it can be accessed on. You can navigate to this in a browser to see
the example application.

You will also need to run an MHS (see the `mhs` project) in order to handle the messages generated.
