
####__**111 Receiver Proof of Concept**__

This module includes a basic example of a 111 receiver implemented to help identify the complexities
of implementing a 111 receiver and analyse the effectiveness of the ITK testbench as a development aid. As
a mock receiver the roll of this end point is to receive messages from a 111 Post Event Message (PEM) sender, 
validate the message against the specification outlined in the ITK conformance document and respond to the sender
appropriately.

####**Usage**
This module can be cloned and the requirements installed using pipenv, the tests can be run using:
`pipenv run tests`
