import json
from unittest import TestCase
import os
import requests


def get_target_address():
    return os.getenv('SCR_SERVICE_ADDRESS', 'http://localhost:9000')


class SCREndpointTest(TestCase):

    def test_scr_happy_path(self):
        body = {"yes": ["one"]}
        response = requests.post(f"{get_target_address()}/gpsummaryupload",
                                 data=json.dumps(body))
        self.assertEqual(json.loads(response.text), body)
