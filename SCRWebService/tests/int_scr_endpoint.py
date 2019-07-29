import json
from unittest import TestCase
import os
import requests


def get_target_address():
    return "http://localhost:9000"
    # return os.environ['SCR_SERVICE_ADDRESS']


class SCREndpointTest(TestCase):

    def test_scr_happy_path(self):
        body = {"yes": ["one"]}
        response = requests.post(f"{get_target_address()}/scr",
                                 data=json.dumps(body))
        print(response.text)
        self.assertEqual(json.loads(response.text), body)