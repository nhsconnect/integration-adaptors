import abc


class AbstractMHSCacheAdaptor(abc.ABC):

    def __init__(self, expiry_time=15):
        """
        :param expiry_time: Time for a value to expire in minutes
        """
        self.expiry_time = expiry_time
        pass

    @abc.abstractmethod
    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str):
        """
        Given a key the cache should return either the cached value or None if the value is not found or if the value is
        out of date
        :param ods_code:
        :param interaction_id:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_cache_value(self, ods_code: str, interaction_id: str, value):
        """

        :param ods_code:
        :param interaction_id:
        :param value:
        :return:
        """
        raise NotImplementedError()
