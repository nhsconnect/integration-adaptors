import mhs.routing.abstract_cache_adapter as ACA
import time


def _generate_key(ods_code: str, interaction_id: str):
    return ods_code + interaction_id


class DictionaryCache(ACA.AbstractMHSCacheAdaptor):

    def __init__(self, expiry_time=15):
        if expiry_time < 0:
            raise ValueError('Invalid expiry time, must be non-negative')
        self.cache = {}
        super().__init__(expiry_time)

    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str):
        key = _generate_key(ods_code, interaction_id)

        if key in self.cache and not self._value_is_expired(key):
            if self._value_is_expired(key):
                self.cache[key] = None
                return None
            else:
                return self.cache[key]['value']

        return None

    def _value_is_expired(self, key: str):
        current_time = time.time()
        insert_time = self.cache[key]['time']
        if current_time - insert_time > self.expiry_time:
            return True
        return False

    async def add_cache_value(self, ods_code: str, interaction_id: str, value):
        key = _generate_key(ods_code, interaction_id)
        insert_time = time.time()
        self.cache[key] = {
            'time': insert_time,
            'value': value
        }
