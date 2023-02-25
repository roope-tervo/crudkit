import requests, string, inspect
from functools import wraps
from urllib.parse import urlparse

# pull relevant argument keys from requests.Request constructor
req_argnames = inspect.getfullargspec(requests.Request)[0]


class requestSessionStrategy:
    def __call__(self, all_kwargs):

        session = all_kwargs.get("session", requests.Session())

        request_kwargs = extract_request_params(all_kwargs)

        r = session.request(**request_kwargs)
        r.raise_for_status()
        return r


def is_url(url, *args):
    if not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def _extract_first(data, test=lambda x, _: x != None, default=None):
    return next((x for x in iter(data) if test(x, data)), default)


def extract_request_params(kwargs):
    """extract from kwargs & args all parameters that can be relevant for the method `requests.request`"""
    # first positional argument can be the url

    if (
        all(True for k in ["path", "base_url"] if kwargs.get(k) != None)
        and kwargs.get("url") == None
    ):
        kwargs["url"] = kwargs["base_url"] + kwargs["path"]

    relevant_kwargs = {key: value for key, value in kwargs.items() if key in req_argnames}
    return relevant_kwargs


def template(d, extra_vars={}):
    """template all dict values that are strings and contain the delimiter $"""
    templatable_keys = [key for key, value in d.items() if isinstance(value, str) and "$" in value]
    # print(templatable_keys)
    return {
        **{
            k: string.Template(d[k]).safe_substitute(**{**d, **extra_vars})
            for k in templatable_keys
        },
        **{k: v for k, v in d.items() if k not in templatable_keys},
    }


def request_dec_factory():

    # decorators module
    def request(*top_args, strategy=requestSessionStrategy(), **top_kwargs):
        """override to create the actual resource's read definition"""

        if "path" not in top_kwargs:
            top_kwargs["path"] = next(
                (x for x in iter(top_args) if is_url(x)), top_kwargs.get("path", None)
            )
        if "url" not in top_kwargs:
            top_kwargs["url"] = next(
                (x for x in top_args if is_url(x)), top_kwargs.get("url", None)
            )

        def read_decorator(f):
            """receives the function to be decorated and returns a wrapper function, performing pre-processing of arguments and
            http request to retrieve data for the wrapped function"""

            @wraps(f)
            def new_f(*args, **kwargs):
                """warpper function that is called in place of the wrapped function"""

                (
                    arg_keys,
                    vararg_key,
                    varkw_key,
                    arg_defaults,
                    kwonlyargs,
                    kwonlydefaults,
                    annotations,
                ) = inspect.getfullargspec(f)

                print(f.__code__)

                # also use defaults from target function definition here automagically

                target_defaults = {}
                if arg_defaults != None:
                    target_defaults = {
                        key: value for key, value in zip(reversed(arg_keys), reversed(arg_defaults))
                    }

                all_kwargs = {**target_defaults, **top_kwargs, **kwargs}

                # args to be passed to decorated (wrapped) function
                wrapped_args = []
                wrapped_kwargs = []

                # # check if decorating method instead of plain function
                maybe_self = next(iter(args), None)

                # do this by seeing if the first positional is a class instance
                # & the class contains the definition of the decorated function
                is_self = (
                    inspect.isclass(type(maybe_self))
                    and len(
                        inspect.getmembers(maybe_self, predicate=lambda m: inspect.unwrap(m) == f)
                    )
                    != 0
                )

                if is_self:
                    wrapped_args.append(maybe_self)
                    # decorator was used on a method since the first argument
                    # contains a class instance whose member is the __wrapped__ of f

                    # try to read attributes stashed by @crud.resource
                    ctx = getattr(maybe_self, "__crud_ctx", {})
                    # get defaults (overrides locally allowed)
                    all_kwargs = {**ctx, **all_kwargs}

                # template keyword args
                all_kwargs = template(all_kwargs)

                # no **kwargs specified so only pass relevant keyword args to wrapped function
                if varkw_key == None:
                    wrapped_kwargs = {
                        key: value for key, value in all_kwargs.items() if key in arg_keys
                    }
                else:
                    wrapped_kwargs = all_kwargs

                print("going to strategy", all_kwargs)

                r = strategy(all_kwargs)

                wrapped_args = [*args, r]

                return f(*wrapped_args, **wrapped_kwargs)

            return new_f

        return read_decorator

    return request
