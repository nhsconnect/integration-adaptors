import abc
from abc import ABC


class DbWrapper(ABC):

    @abc.abstractmethod
    def get_all_records_in_table(self) -> list:
        """
        Returns all the records in the DB instance within the given table name
        :return: the records within the collection
        """
        pass

    @abc.abstractmethod
    def clear_all_records_in_table(self) -> None:
        """
        Deletes all records in the DB instance within the given collection
        :return: None
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_state_table_wrapper():
        pass

    @staticmethod
    @abc.abstractmethod
    def get_sync_async_table_wrapper():
        pass
