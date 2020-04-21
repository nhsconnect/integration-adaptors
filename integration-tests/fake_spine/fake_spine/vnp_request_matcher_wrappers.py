from fake_spine.request_matching import RequestMatcher


def async_express():
    return RequestMatcher('async-express-vnp',
                          lambda request: '<eb:Action>QUPC_IN160101UK05</eb:Action>' in request.body.decode())


def async_reliable():
    return RequestMatcher('async-reliable-vnp',
                          lambda request: '<eb:Action>REPC_IN150016UK05</eb:Action>' in request.body.decode())


def sync():
    return RequestMatcher('sync-vnp',
                          lambda request: '<wsa:Action>urn:nhs:names:services:pdsquery/QUPA_IN040000UK32</wsa:Action>' in request.body.decode())


def forward_reliable():
    return RequestMatcher('forward-reliable-vnp',
                          lambda request: '<eb:Action>COPC_IN000001UK01</eb:Action>' in request.body.decode())
