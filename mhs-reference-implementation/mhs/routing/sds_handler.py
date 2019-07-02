import mhs.routing.sds as sds


class MHSAttributeLookupHandler:

    def __init__(self, client: sds.SDSClient):
        if not client:
            raise ValueError('sds client required')
        self.sds_client = client

    async def retrieve_mhs_attributes(self, org_code, interaction_id):
        endpoint_details = await self.sds_client.get_mhs_details(org_code, interaction_id)
        return endpoint_details
