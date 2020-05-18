# MHS Adaptor

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

The MHS Adaptor implements a messaging standard called the External Interface Specification, which defines in some detail a number patterns for
transport layer communication with the Spine. The intent of this MHS Adaptor is to hide this implementation detail from the supplier, and so
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
In this repository, DynamoDB and MongoDB are used as an implementations of the State database.
- Sync-Async Response Database, a special case of the state database where a synchronous facade is provided by the Outbound Service for interactions
with Spine which actually involve asynchronous responses. This database is used to correlate request to Spine and responses from Spine in this scenario. 
Again this is implemented here as a DynamoDB and MongoDB state adaptor.
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

## API Documentation

The MHS Adaptor presents a simple HTTP synchronous interface which is used to make requests to Spine.

Please refer to the [API Documentation](outbound/openapi-docs.html) for further details.

Examples of how this API is called can be found in the [integration tests](../integration-tests/integration_tests) module

## RestClient collection- example requests to the MHS Adaptor

A RestClient collection [rest-client/mhs](../rest-client/mhs) illustrates how the MHS Adaptor API
is called. This collection provides following API request examples:
 - asynchronous request to outbound, with no retries while sending requests from outbound to spine
 - asynchronous request to outbound, with retries while sending request from outbound to to spine
 - synchronous request to outbound, with retries while sending request to nhs application other than spine
 - synchronous request to outbound
 - solicited request to inbound
 - unsolicited request to inbound.
 
There are also health, reliability and routing checks.
 
Before sending these requests, you will need to create a setting.json file as described in [README](../rest-client/README.md).
 
Before sending requests directly to the inbound service, you will need to switch off ssl by setting 'MHS_INBOUND_USE_SSL: false' in .yaml inbound configuration file.
It is necessary to send requests to inbound without ssl.  

#### "Async Express Pattern Message  - Synchronous Response" 

The Asynchronous Express Messaging Pattern is one of the Spine messaging patterns which is defined in the Spine External Interface Specification. 
In this pattern, a request is made to Spine, but the response is not provided on the same connection. Instead, spine initiates a connection back to your 
MHS with the response. I.e the response from Spine is delivered like a call back to your MHS. The MHS Adaptor has hidden all this asynchronous callback 
detail behind a synchronous interface, so your HTTP client just sees a simple HTTP request/response. This is what the MHS Adaptor has termed the "Sync-Async wrapper". 
When you set the `wait-for-response` message header to `true` you are requesting the MHS Adaptor to hide this asynchronous response from you, and deliver the response in the 
same HTTP connection.

In this example, the `QUPC_IN160101UK05` Spine message is used. This Spine message is used when requesting the Summary Care Record of a patient.
 
#### "Async Express Pattern Message  - Asynchronous Response" 

The Asynchronous Express Messaging Pattern is one of the Spine messaging patterns which is defined in the Spine External Interface Specification. 
In this pattern, a request is made to Spine, but the response is not provided on the same connection. Instead, spine initiates a connection back 
to your MHS with the response. I.e the response from Spine is delivered like a call back to your MHS.

The MHS Adaptor has hidden all this asynchronous callback detail behind a synchronous interface, so your HTTP client just sees a simple HTTP 
request/response. This is what the MHS Adpator has termed the Sync-Async wrapper. When you set the wait-for-response  message header you are requesting 
the MHS Adaptor to hide this asynchronous response from you, and deliver the response in the same hTTP connection.

In this example, the `QUPC_IN160101UK05` Spine message is used again. 

## AWS Exemplar

It is expected that the MHS solution will be deployed in a number of differing public and private cloud environments.
In view of this, an exemplar of one specific instance of deployment into a cloud environment has been
create, based on AWS.

This demonstrates a recommended blueprint of deployment of the necessary assets which results in a 
security, scalable and highly available architecture. Automated deployment of this architecture has
been implemented through Terraform.

The diagram below illustrates the AWS exemplar:

[MHS - AWS Exemplar Deployment](../documentation/MHSAWSDeploymentDiagram.pdf)

Key points to note:
 - The MHS Adaptor is deployed within a custom VPC
 - A separate custom VPC, the "Supplier Client System" VPC represents the existing AWS resources which the supplier
 runs in AWS - connectivity with the MHS VPC is via VPC peering. 
 - A third VPC "OpenTest VPN VPC" is shown as an optional element in the exemplar where connectivity to
 NHS Digital's OpenTest testing platform is required.
 - ECS is used as the container orchestration service.
 - ECS Fargate is used as the ECS launch type as this removes concerns around management of the underlying hosts 
 on which services and tasks execute
 - ECR is used to store docker images required by the Fargate clusters to run instances of the services.
 - Each of the service described in the software architecture diagram above have been implemented as 
 an ECS cluster. A configurable number of instances of each ECS Task can run in each cluster.
 - Instances of ECS Tasks are balanced automatically across multiple Availability Zones
 - Balancing of load across instances of the outbound service and the routing service has been implemented 
 through the use of an Application Load Balancer
 - Balancing of load across instances of the inbound service has been implemented throught the
 use of a Network Load Balancer to enable the inbound service itself to implement TLS mututal
 authentication.
 - DynamoDB and MongoDB are used to implement the state database and sync-re-sync database.
 - Elasticache for Redis HA is used to implement the routing and reliability cache which is a dependency
 of the routing service.
 - Cloudwatch is used as the logging
 - VPC endpoints are used throughout to ensure traffic does not traverse the public internet.
 - Amazon MQ is used as an example of an AMQP compliant message queue to which Spine messages 
 can be sent. This will occur where an "unsolicited inbound" message is received from Spine which must be 
 passed directly to the supplier system, or where a supplier has chosen to receive a response from Spine
 asynchronously.

### Terraform for AWS Exemplar

The [pipeline](../pipeline/) directory contains Terraform resources which use the AWS provider for Terraform.

## Further Exemplars

A future phase of MHS adaptor work will deliver an Azure public cloud exemplar. This will be based on the 
AWS blueprint architecture, with modifications focusing on differences in cloud services such as the use
of ACS for container orchestration.

## Operating the MHS Adaptor in your infrastructure

Refer to [Operating the MHS Adaptor](operating-mhs-adaptor.md) for information on how to operate the MHS Adaptor as it is deployed
within the boundary of your infrastructure.

## Developer Setup

For information targeted at developers making use of the MHS Adaptor, please refer to [MHS Adaptor developer notes](mhs-adaptor-dev-notes.md). 
This includes information on how to [test-drive the MHS Adaptor on a local development machine](running-mhs-adaptor-locally.md). 
