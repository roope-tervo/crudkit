from .request import request_dec_factory
from .session import session
from .resource import resource


def request(*args, **kwargs):
    return request_dec_factory()(*args, **kwargs)


def get(*args, **kwargs):
    kwargs = {"method": "GET", **kwargs}
    return request_dec_factory()(*args, **kwargs)


def put(*args, **kwargs):
    kwargs = {"method": "PUT", **kwargs}
    return request_dec_factory()(*args, **kwargs)


def post(*args, **kwargs):
    kwargs = {"method": "POST", **kwargs}
    return request_dec_factory()(*args, **kwargs)


def delete(*args, **kwargs):
    kwargs = {"method": "DELETE", **kwargs}
    return request_dec_factory()(*args, **kwargs)
