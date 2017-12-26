import datetime as _datetime
import functools as _functools
import logging as _logging
import typing as _typing

_log = _logging.getLogger(__name__)


def _throttle(seconds):
    throttle_period = _datetime.timedelta(seconds=seconds)

    def throttle_decorator(fn):
        time_of_last_call = _datetime.datetime.min

        @_functools.wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal time_of_last_call
            now = _datetime.datetime.now()
            if now - time_of_last_call > throttle_period:
                time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper

    return throttle_decorator


def log_entry_and_exit(log_callable: _typing.Callable):
    """Log entry and exit of the decorated function"""

    def decorator(inner):

        @_functools.wraps(inner)
        def wrapped(*args, **kwargs):
            log_callable('enter %s', inner.__name__)
            try:
                r = inner(*args, **kwargs)
            except Exception as ex:
                log_callable('exit %s with error: %s', inner.__name__, ex)
                raise
            else:
                log_callable('exit %s', inner.__name__)
            return r

        return wrapped

    return decorator


@_throttle(2)
def throttled_log(log_callable: _typing.Callable, msg: str,
                  *args: _typing.Any, **kwargs: _typing.Any):
    return log_callable(msg, *args, **kwargs)
