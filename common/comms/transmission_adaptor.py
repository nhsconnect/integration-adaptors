import abc


class TransmissionAdaptor(abc.ABC):

    @abc.abstractmethod
    async def make_request(self,  interaction_details, message):
        """Given a set of interaction details and a message, the message is propagated to the appropriate
        endpoint along with the necessary headers"""
        pass
