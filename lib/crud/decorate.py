import requests, string, inspect
from functools import wraps
from urllib.parse import urlparse
from .strategy import NoopStrategy


def is_url(url, *args):
    if not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def template(d, extra_vars={}):
    """template all top level dict properties that are strings by type, and contain the delimiter character $"""
    templatable_keys = [key for key, value in d.items() if isinstance(value, str) and "$" in value]
    # print(templatable_keys)
    return {
        **{
            k: string.Template(d[k]).safe_substitute(**{**d, **extra_vars})
            for k in templatable_keys
        },
        **{k: v for k, v in d.items() if k not in templatable_keys},
    }


def decorate(strategy=NoopStrategy()):
    """decorator factory function"""

    def request(*top_args, strategy=strategy, **top_kwargs):
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

                # also use defaults from target function definition here automagically
                # (so they are taken into account when templating string params!)

                target_defaults = {}
                if arg_defaults != None:
                    target_defaults = {
                        key: value for key, value in zip(reversed(arg_keys), reversed(arg_defaults))
                    }

                all_kwargs = {**target_defaults, **top_kwargs, **kwargs}

                # args to be passed to decorated (wrapped) function
                wrapped_args = []
                wrapped_kwargs = []

                # # check if decorating method instead of plain function, grab first argument to wrapped function
                maybe_self = next(iter(args), None)

                # check method status of wrapped function by seeing if the first positional is a class instance,
                # AND also that the class instance in question contains the decorated function as a member
                is_self = (
                    inspect.isclass(type(maybe_self))
                    and len(
                        inspect.getmembers(maybe_self, predicate=lambda m: inspect.unwrap(m) == f)
                    )
                    != 0
                )

                if is_self:
                    # decorator was used on a method since the first argument
                    # contains a class instance whose member is the __wrapped__ of f, so we should pass the instance on as-is.
                    wrapped_args.append(maybe_self)

                    # try to read attributes stashed by @crud.resource
                    ctx = getattr(maybe_self, "__crud_ctx", {})

                    # get default values for any parameters of the wrapped function from the class-level crud.resource decorator here
                    all_kwargs = {**ctx, **all_kwargs}

                # template all keyword arguments, can be suppressed
                if top_kwargs.get("do_template", True):
                    all_kwargs = template(all_kwargs)

                # no **kwargs specified in definition of wrapped function, so we should only pass accepted keyword arguments to avoid errors!
                if varkw_key == None:
                    wrapped_kwargs = {
                        key: value for key, value in all_kwargs.items() if key in arg_keys
                    }
                else:
                    wrapped_kwargs = all_kwargs

                r = strategy(all_kwargs)

                wrapped_args = [*args, r]

                return f(*wrapped_args, **wrapped_kwargs)

            return new_f

        return read_decorator

    return request
