from __future__ import annotations


class RoutingResponse(object):

    def __init__(self):
        self.mhs_endpoint = "https://fakespine"
        self.mhs_party_key = "party-key-default"
        self.mhs_cpa_id = "cpa-id-default"
        self.unique_identifier = "123456"

    def override_mhs_end_point(self, mhs_endpoint: str) -> RoutingResponse:
        self.mhs_endpoint = mhs_endpoint
        return self

    def override_mhs_part_key(self, mhs_party_key: str) -> RoutingResponse:
        self.mhs_party_key = mhs_party_key
        return self

    def override_mhs_cpa_id(self, mhs_cpa_id: str) -> RoutingResponse:
        self.mhs_cpa_id = mhs_cpa_id
        return self

    def override_unique_identifier(self, unique_identifier: str) -> RoutingResponse:
        self.unique_identifier = unique_identifier
        return self

    def get_response(self) -> dict:
        return {
            "nhsMHSEndPoint": [self.mhs_endpoint],
            "nhsMHSPartyKey": self.mhs_party_key,
            "nhsMhsCPAId": self.mhs_cpa_id,
            "uniqueIdentifier": [self.unique_identifier]
        }
