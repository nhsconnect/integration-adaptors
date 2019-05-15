import requests


def call_mhs(mhs_command, hl7payload):
    mhs_url = 'http://localhost/' + mhs_command
    response = requests.post(mhs_url, data=hl7payload)

    return response.text
