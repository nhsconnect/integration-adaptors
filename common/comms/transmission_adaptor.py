import abc


class TransmissionAdaptor(abc.ABC):

    def make_request(self,  interaction_details, message):
        """Given a set of interaction details and a message, the message is propogated to the appropriate
        endpoint along with the necessary headers"""
        pass
