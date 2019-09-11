from typing import Union

import tornado
import tornado.httputil
import tornado.testing
import tornado.web

ORG_CODE = "org"
SERVICE_ID = "service"


def test_get_handles_missing_params(self):
    with self.subTest("Missing Org Code"):
        response = self.fetch(self.build_url(org_code=None, service_id=SERVICE_ID), method="GET")

        self.assertEqual(response.code, 400)

    with self.subTest("Missing Service ID"):
        response = self.fetch(self.build_url(org_code=ORG_CODE, service_id=None), method="GET")

        self.assertEqual(response.code, 400)

    with self.subTest("Missing Org Code & Service ID"):
        response = self.fetch(self.build_url(org_code=None, service_id=None), method="GET")

        self.assertEqual(response.code, 400)


def build_url(org_code: Union[None, str] = ORG_CODE, service_id: Union[None, str] = SERVICE_ID):
    url = "/"
    args = {}

    if org_code is not None:
        args["org-code"] = org_code

    if service_id is not None:
        args["service-id"] = service_id

    url = tornado.httputil.url_concat(url, args)
    return url
