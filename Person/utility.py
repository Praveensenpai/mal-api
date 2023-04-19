from functools import wraps


def exception_handler(return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TypeError:
                return return_value

        return wrapper

    return decorator
