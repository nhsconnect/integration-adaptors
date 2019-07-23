# National Integration Adaptor

This repository contains adaptors which accelerate integration with national NHS systems.

These adaptors hide the complexity of integration with the interfaces provided by the current national systems by
implementing an adaptor layer. The integrating supplier sees only a simplified and standardised set of interfaces which
the adaptor layer presents. The adaptor layer is responsible for interacting with the legacy NHSD interface estate. 

![High Level Architecture](documentation/High%20Level%20Architecture.png)

As a result, the complexity of integration work is much reduced. The integrating supplier is required to implement a
minimum set of client types in their interface layer and can re-use this code across multiple integrations.
