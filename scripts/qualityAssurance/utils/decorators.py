from functools import wraps


def ifNoErrorsReturn(argument):
    """
    If the error list is emtpy return the argument provided.

    :param argument:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.errors:
                return argument

            return func(self, *args, **kwargs)
        return wrapper
    return decorator
