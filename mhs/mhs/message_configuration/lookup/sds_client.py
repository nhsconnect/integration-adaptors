"""This module contains the client used to make requests to SDS."""


class SDSClient:
    """A client that can be used to query SDS."""

    async def get_mhs_details(self, ods_code: str, interaction_id: str) -> Dict:
        """
        Returns the mhs details for the given org code and interaction ID.

        :return: Dictionary of the attributes of the mhs associated with the given parameters
        """
        pass
