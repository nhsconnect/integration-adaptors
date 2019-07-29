import json
from unittest import TestCase

import requests


class SCREndpointTest(TestCase):

    def test_scr_happy_path(self):
        body = {"yes": ["one"]}
        response = requests.post("http://localhost:9000/scr",
                                 data=json.dumps(body))
        print(response.text)
        self.assertEqual(json.loads(response.text), body)