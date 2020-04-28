from abc import ABC

import tornado.web

from fake_spine.tracking_ids_headers_reader import read_tracking_id_headers


class BaseHandler(tornado.web.RequestHandler, ABC):
    """A base handler for fake spine"""

    def initialize(self, **kwargs) -> None:
        read_tracking_id_headers(self.request.headers)
