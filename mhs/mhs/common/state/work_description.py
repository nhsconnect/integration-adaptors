# from typing import S
import enum
import json


class MessageStatus(enum.Enum):
    RECEIVED = 1
    STARTED = 2
    IN_OUTBOUND_WORKFLOW = 3
    

class WorkDescription(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def publish(self):
        x = json.loads(self.items())
        print(x)


class WorkDescriptionFactory:

    @staticmethod
    def get_work_description_from_store(persistence_store, message_id):
        json_store_data = persistence_store.get('default_table', message_id)







