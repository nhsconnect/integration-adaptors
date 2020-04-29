
import tornado.web

from utilities import timing


class RemovalRequestHandler(tornado.web.RequestHandler):

    @timing.time_request
    async def post(self, patient_id):
        self.set_status(202)
        await self.finish(f'Removal for patient {patient_id}')