from .decorate import decorate
from .session import session
from .resource import resource

from .strategy import RequestSessionStrategy


def request(*args, **kwargs):
    return decorate(strategy=RequestSessionStrategy())(*args, **kwargs)


def get(*args, **kwargs):
    """"""
    kwargs = {"method": "GET", **kwargs}
    return decorate(strategy=RequestSessionStrategy())(*args, **kwargs)


def put(*args, **kwargs):
    kwargs = {"method": "PUT", **kwargs}
    return decorate(strategy=RequestSessionStrategy())(*args, **kwargs)


def post(*args, **kwargs):
    kwargs = {"method": "POST", **kwargs}
    return decorate(strategy=RequestSessionStrategy())(*args, **kwargs)


def delete(*args, **kwargs):
    kwargs = {"method": "DELETE", **kwargs}
    return decorate(strategy=RequestSessionStrategy())(*args, **kwargs)
