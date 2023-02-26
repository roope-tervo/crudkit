from functools import wraps


def resource(**top_kwargs):
    """decorator for classes, will inject decorator kwargs to class instance under attribute __crud_ctx"""

    def resource_decorator(init):
        @wraps(init)
        def wrapper_init(*args, **kwargs):
            instance = init(*args, **kwargs)
            instance.__crud_ctx = {}

            for key, value in top_kwargs.items():
                if value != None:
                    instance.__crud_ctx[key] = value

            return instance

        return wrapper_init

    return resource_decorator
