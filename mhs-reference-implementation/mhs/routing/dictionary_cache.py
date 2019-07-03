import mhs.routing.abstract_cache_adapter as ACA
import time
from typing import Dict, Optional

FIFTEEN_MINUTES_IN_SECONDS = 900


def _generate_key(ods_code: str, interaction_id: str):
    return ods_code + interaction_id


class DictionaryCache(ACA.AbstractMHSCacheAdaptor):

    def __init__(self, expiry_time: float = FIFTEEN_MINUTES_IN_SECONDS):
        if expiry_time < 0:
            raise ValueError('Invalid expiry time, must be non-negative')
        self.cache = {}
        super().__init__(expiry_time)

    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str) -> Optional[Dict]:
        key = _generate_key(ods_code, interaction_id)

        if key in self.cache and not self._is_value_expired(key):
            if self._is_value_expired(key):
                self.cache[key] = None
                del self.cache[key]
                return None
            else:
                return self.cache[key]['value']

        return None

    def _is_value_expired(self, key: str) -> bool:
        current_time = time.time()
        insert_time = self.cache[key]['time']
        if current_time - insert_time > self.expiry_time:
            return True
        return False

    async def add_cache_value(self, ods_code: str, interaction_id: str, value) -> None:
        key = _generate_key(ods_code, interaction_id)
        insert_time = time.time()
        self.cache[key] = {
            'time': insert_time,
            'value': value
        }
