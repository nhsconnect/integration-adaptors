# MHS

This package contains a pre-assured implementation of a Message Handling Service (MHS), intended to encapsulate the
details of Spine messaging and provide a simple interface to allow HL7 messages to be sent to a remote MHS.

## Introduction - What is an MHS?

The NHS Spine is "a collection of national applications, services and directories which support the health and social care sector in the 
exchange of information in national and local IT systems. A national, central service that underpins the NHS Care Records Service". 
It provides applications such as the Personal Demographics Service (PDS) and also supports intermediary communication between other systems 
(such as the transfer of patient records between GP practices when a patient moves practice). 

A Message Handling Service (MHS) is a component which is required in order to communicate with Spine. Spine can be considered a "hub", whereas
systems wishing to communicate with this hub need to implement an MHS. Technically speaking, the central hub is also a MHS, but is the central 
hub in this hub-spoke architecture.

The MHS implements a messaging standard called the External Interface Specification, which defines in some detail a number patterns for
transport layer communication with the Spine. The intent of this MHS adaptor is to hide this implementation detail from the supplier, and so
make it easier to connect to Spine and perform business operations such as interacting with Spine services like PDS.

## Software Architecture

The following diagram provides a view of the services (run in docker containers) and Python modules which make up the MHS Adaptor:

[MHS Adaptor Logical Architecture](../documentation/MHSLogicalArchitecture.pdf)

The MHS adaptor is composed of three main services, coloured in orange,  which are executed in Docker containers:
1. The MHS Outbound Service which is responsible for listening for requests from the wider local system context and transmitting these to Spine
2. Spine Route Lookup, which is used to lookup routing and reliability information from Spine's directory service.
3. the MHS Inbound Service which is responsible for listening for incoming requests from Spine.

These services have some dependencies, shown in blue, which are implemented through the adaptor pattern:
- State database, which is used to handle internal MHS message state. 
In this repository, DynamoDB is used as an implementation of the State database.
- Sync-Async Response Database, a special case of the state database where a synchronous facade is provided by the Outbound Service for interactions
with Spine which actually involve asynchronous responses. This database is used to correlate request to Spine and responses from Spine in this scenario. 
Again this is implemented here as a DynamoDB state adaptor.
- Container orchestration. The container orchestration solution of your choice can be used. In this repository, Docker compose is used when running
the adaptor locally, and ECS, Fargate and ECR are used by the AWS exemplar architecture.
- Secret Store - Used to safely inject secrets such as passwords into running containers.
- Log and Audit Store - Running containers log to STDOUT and therefore logs can be captured and forwarded to the logginc and auditing solution of your choice.
- Inbound Queue - Where unsolicited messages are received from Spine, these are placed on an AMQP compliant queue for processing by the local system.
When running locally, this solution makes use of RabbitMQ, whereas the AWS Exemplar uses AmazonMQ as an AMQP compliant message queue.
- Load Balancers are shown balancing load to the Inbound and outbound services. The AWS exemplar demonstrates the use of Application Load Balancers and
Network Load Balancers to implement this.
- Directory cache which acts as a cache for frequently requested routing and reliability information. Locally implemented through Redis, this is 
also demonstrated through Elasticache for Redis in AWS.

The National Adaptors Common Module provides classes which implement common requirements leveraged by multiple services or modules.

## Note on Certificate Validation 

**WARNING: Due to the limitations of NHS Digital OpenTest configuration, verification of the server certificate received when making a connection 
to the spine MHS is currently DISABLED (see the [OutboundTransmission](./outbound/outbound/transmission/outbound_transmission.py) class'
`make_request` method).** This MHS should not be used in a production environment unless this certificate verification
is re-enabled.


## Developer Setup

For information targeted at developers making use of the MHS Adaptor, please refer to [MHS Adaptor deveoper notes](running-mhs-adaptor-locally.md)

