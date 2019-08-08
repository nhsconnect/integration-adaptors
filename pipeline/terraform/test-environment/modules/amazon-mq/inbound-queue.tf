resource "aws_mq_broker" "inbound-queue" {
  broker_name = "${var.environment}-inbound-queue"

  configuration {
    id       = aws_mq_configuration.inbound-queue-configuration.id
    revision = aws_mq_configuration.inbound-queue-configuration.latest_revision
  }

  engine_type        = "ActiveMQ"
  engine_version     = "5.15.9"
  host_instance_type = "mq.t2.micro"
  security_groups    = var.security_group_ids

  user {
    username = "ExampleUser"
    password = "MindTheGap"
  }
}


resource "aws_mq_configuration" "inbound-queue-configuration" {
  description    = "Inbound queue configuration."
  name           = "${var.environment}-inbound-queue-configuration"
  engine_type    = "ActiveMQ"
  engine_version = "5.15.9"

  data = <<DATA
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<broker xmlns="http://activemq.apache.org/schema/core">
  <destinationPolicy>
    <policyMap>
      <policyEntries>
        <policyEntry topic="&gt;" gcInactiveDestinations="true" inactiveTimoutBeforeGC="600000">
          <pendingMessageLimitStrategy>
            <constantPendingMessageLimitStrategy limit="1000"/>
          </pendingMessageLimitStrategy>
        </policyEntry>
        <policyEntry queue="&gt;" gcInactiveDestinations="true" inactiveTimoutBeforeGC="600000" />
        </policyEntries>
    </policyMap>
  </destinationPolicy>
  <plugins>
    <forcePersistencyModeBrokerPlugin persistenceFlag="true"/>
    <statisticsBrokerPlugin/>
    <timeStampingBrokerPlugin ttlCeiling="86400000" zeroExpirationOverride="86400000"/>
  </plugins>
</broker>
DATA
}