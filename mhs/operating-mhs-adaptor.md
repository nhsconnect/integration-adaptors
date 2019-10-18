# Operating the MHS Adaptor

This following is a guide to operational considerations where the MHS Adaptor is deployed within your infrastructure

## Log consumption
The MHS services emit logs and audit records on standard I/O streams, following [The Twelve Factor App](http://12factor.net) guidance on [logging](https://www.12factor.net/logs). Logs within the MHS Adaptor context are therefore captured 
by the Docker containers they are hosted within. Whichever Docker container orchestration technology is used, these log streams can be captured and/or 
forwarded to an appropriate log indexing service for consumption, storage and subsequent query.

The [AWS exemplar](README.md#aws-exemplar) deployment of the MHS Adaptor makes use of the ECS Fargate service and the logs are captured into the 
CloudWatch Logs service. Additionally logs produced by other cloud infrastructure such as load balancers are also captured into the CloudWatch Logs service, 
so that logs are comprehensively captured across the whole solution allowing for joined up querying.

## Choice of Log analytics tooling
The MHS Adaptor may be deployed into various public or private cloud platforms. Irrespective of the platform, logs should be forwarded to a suitable log 
indexing service. 

### Key requirements for choice of logging tool

Key requirements that should be prioritised when choosing a service for log indexing, storage, query and analytics are:

- Ability to parse key-value pairs in log lines and infer/interpret the data types of values
- Ability to build complex queries which filter and/or aggregate values using those key-value pairs
- Ability to index and present log records in time series order with timestamp values interpreted to the full accuracy present in the logs (e.g. millisecond)
- Ability to tie together multiple logs for flow analysis across multiple components using a common correlation ID
- Facilities to calculate aggregate metrics, such as moving averages or totals, across a defined set of log messages.
- Facilities for graphing, dashboard creation and analytical interaction with the presented data
- Ability to implement a log retention policy, including log rotation, and full deletion of "rolled" logs
- Secure storage and handling of log data
- Role based access control including the ability to differentiate groups of logs for more strict permissions and restrict access to audit logs to a specific group of users
- Backup to cold storage
- Ability to raise alerts that notify subscribed users immediately upon certain events happening such as presence of specific types of log, or breach of thresholds.
- Ability to highlight and alert on the absence of log data from an expected component, indicating a component silently failing.

Some guidance for public cloud deployments are given below:

#### AWS deployments

 - CloudWatch Logs is a common choice for log indexing for AWS deployments.
 - Logs indexed in CloudWatch Logs can be queried and analysed using the AWS tool CloudWatch Logs Insights.
 - If Splunk is your organisation's preferred log analysis tool, there are a number of methods for integrating Splunk with CloudWatch Logs including the 
   Splunk AWS Add-on, the use of AWS Kinesis or AWS Lambdas to forward logs, or by querying the CloudWatch Logs Insights API.
 - Other solutions such as DataDog, New Relic, Grafana, Elastic Stack, or Prometheus offer similar tools for monitoring, calculating metrics, graphing and creating dashboards and alerting. 
   These tools all have modes of integration with CloudWatch Logs.

#### Azure deployments

 - Azure Monitor is a common choice for log indexing for Azure deployments:
    - Comprises of a suite of services for log and metric capture and storage, alerting, analysis, visualisation and dashboard creation 
   and the creation of insights.
    - APIs for integration of other tools.
    - Features designed for specific patterns of cloud deployment, including capabilities tailored to Containers hosted in Azure Kubernetes Service.
    - Microsoft's Power BI tool can be configured to automatically import data from Azure Monitor for more business-centric analytics.
    - Other solutions such as DataDog, AppDynamics, Elastic Stack, Grafana, NewRelic, SolarWinds, Splunk and Sumo Logic can be integrated through Azure Monitor Export APIs.

## Logging Levels

The logs produced by the MHS Alpha application components have one of the following log levels:

| Log Level | Description |
| --------- | ----------- |
| INFO | General information messages and confirmation that things are working as expected. Allows for tracking of work following through the system, points-of-interest, and where uncommon logical flows have been invoked. |
| WARNING | Indication that something unexpected has happened but is being handled, such as processing of an invalid message, invocation of error handling logic which is not expected to be executed through the specified processing. It can also be used to raise a warning about a potential future problem, such as levels or disk space or memory reaching a threshold. When using WARNING, the software is still working as expected, higher log levels are used when this is not the case. |
| ERROR | Due to a more serious error which cannot be handled, the software has not been able to perform some function. This may result in a request erroring or an item of work being unable to be processed further without further intervention and remediation. The application should be able to recover from an ERROR scenario using its error handling logic and continue normal operations, processing other requests/messages without deterioration, if it cannot then a higher log level will be used. |
| CRITICAL | Indicates a problem, which may still be handled by error handling logic, but which is likely to compromise the on-going operation of the component. This is also used where error handling logic has failed and final logs are being produced before the process/service dies. |
| AUDIT | Specific logging of audit events in the business process. See section below for further details of regarding audit logs. |

The MHS application components have specifically chosen INFO as the lowest log level, rather than DEBUG. The principle here is that all information logged is 
potentially useful for diagnosing live issues, and so should be available in Production. It is not recommended to enable DEBUG level logging in production, 
so it is important that the lowest level of logs emitted from the MHS components to facilitate diagnostics is INFO.

The third party libraries used by the MHS Adaptor will likely emit logs at DEBUG if this level has been configured. You should be aware that DEBUG 
level logs from components involved in I/O are **highly likely to include the entire message payload** which in the context of the MHS Adaptor is **likely to 
contain Patient Identifying Data and other sensitive data**. As such it is **strongly recommended that DEBUG log level never be configured on in Production environments**, 
to ensure that real patient data does not leak into log files.

## Log Format

Log messages produced by the MHS are in human readable form and important data is included within the log message as key=value pairs so that they can be parsed 
and used for searching, filtering, agregation, graphing etc.

An example is given below:

```text
[2019-10-10T10:10:00.735207Z] Entered async express workflow to handle outbound message RequestId=459D9095-45F2-4C2D-86EA-E1E0F78BC142 CorrelationId=12345 ProcessKey=ASYNC_EXPRESS_WORKFLOW0001 pid=6 LogLevel=INFO LoggerName=ASYNC_EXPRESS_WORKFLOW
```

- The start of the log line included a datetime-stamp in ISO8601 timestamp format and always in UTC timezone.

- The end of the log line contains some common key=value pairs which can be expected to be present in all log messages:

| Common Key | Purpose |
| ---------- |:------- |
| `ProcessKey` | To identify which logical component of the solution produced the log message and a unique identifier for the log line to aid tracking down the piece of code that produced the log message, e.g. `ASYNC_EXPRESS_WORKFLOW0001`. Each ProcessKey will be unique. |
| `pid`        | Process ID, identifies the running instance of a component that produced the log message. |
| `RequestId` | Identifies what item of work is being processed be it an incoming request, message processed off a queue or batch file being picked up and worked. |
| `CorrelationId` | A unique ID which is generated at the very start of a workflow and is used throughout all log messages related to that work, such that all the logs in the chain can be tied together for a single work item. CorrelationId can be passed into the MHS Adaptor components from the supplier's calling client to allow for the CorrelationId to also tie the workflow together with the client system. |
| `LogLevel` | The level at which the log line was raised. See [Logging Levels](#logging-levels) above. |
| `LoggerName` | Identifies the sub-component within the MHS Adaptor which produced the log line |

## Audit log consumption

Audit logs are emitted through the same channel as other log messages, via the standard I/O streams captured and forwarded by Docker. Audit log messages 
have a log level of AUDIT which is used to differentiate them from other logs. Due to the potential sensitivity of the data held in audit logs and the 
need to ensure that audit logs have stronger controls around them to prevent the possibility of tampering, it is **strongly advised** that the log indexing tooling 
chosen should be configured to filter log lines with an logging level of AUDIT out of the main log bucket and divert them into their own audit log bucket, which can be stored and controlled 
separately.

### Audit log lines

Every outbound and inbound message which passes through the MHS Adaptor results in log lines being generated with log level of AUDIT, as described above. 

The following is an example of the format of an AUDIT log line, identified by the key-value pair `LogLevel=AUDIT`

```text
[2019-10-10T10:10:00.735207Z] Async-express workflow invoked. Message sent to Spine and Acknowledgment=MessageStatus.OUTBOUND_MESSAGE_ACKD received. RequestSentTime=2019-10-10T10:10:00.282734Z AcknowledgmentReceivedTime=2019-10-10T10:10:00.435207Z RequestId=E2EDED45-F6BE-4666-9CAE-AD05618CD559 CorrelationId=12345 ProcessKey=ASYNC_EXPRESS_WORKFLOW0011 pid=6 LogLevel=AUDIT LoggerName=ASYNC_EXPRESS_WORKFLOW
```



