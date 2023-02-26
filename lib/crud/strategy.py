import inspect, requests
from collections.abc import Callable


class NoopStrategy(Callable):
    """no-op strategy that returns nothing, for when you just want to inject/template parameters"""

    def __call__(*args, **kwargs):
        return None


class RequestSessionStrategy(Callable):
    """Strategy can be anything callable. requestSessionStrategy extracts an optional "session"
    property & request.Request-relevant parameters from kwargs passed to the decorated function
    via invoking call, respecting defaults passed via class-level @crud.resource(arg=value,...) call.

    Returns resulting requests.Response object.
    """

    @staticmethod
    def _extract_request_params(kwargs):
        """extract from kwargs & args all parameters that can be relevant for the method `requests.request`"""
        # first positional argument can be the url

        # pull relevant argument keys from requests.Request constructor,
        # so we know which frontloaded arguments to forward to it
        req_argnames = inspect.getfullargspec(requests.Request)[0]

        # "path" & "base_url" are special kwargs that get concatenated if found
        if (
            all(True for k in ["path", "base_url"] if kwargs.get(k) != None)
            and kwargs.get("url") == None
        ):
            kwargs["url"] = kwargs["base_url"] + kwargs["path"]

        relevant_kwargs = {key: value for key, value in kwargs.items() if key in req_argnames}
        return relevant_kwargs

    def __call__(self, all_kwargs):
        "make instance callable as a method"

        # if a Session object is passed via kwargs, use it. Otherwise create a new unconfigured Session.
        session = all_kwargs.get("session", None)

        should_close_session = False
        if not isinstance(session, requests.Session):
            should_close_session = True
            session = requests.Session()

        # we should only allow relevant params to the request method
        request_kwargs = RequestSessionStrategy._extract_request_params(all_kwargs)

        response = session.request(**request_kwargs)

        # don't leave sessions hanging unless caller is explicitly managing them (a session object was provided)
        if should_close_session:
            session.close()

        return response
