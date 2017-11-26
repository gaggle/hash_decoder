import sys
from contextlib import contextmanager
from logging import DEBUG, INFO, getLogger
from typing import Any, Callable, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    import logging

log = getLogger(__name__)


@contextmanager
def log_ctx(msg: str, *args: Any,
            quiet: bool = False,
            verbose: bool = False) -> Iterator:
    if quiet:
        yield
    elif verbose:
        print(msg % args)
        yield
    else:
        print(msg % args + '... ', end='')
        sys.stdout.flush()
        try:
            yield
        except Exception:
            print("ERROR")
            raise
        else:
            print('OK')


_LOG_MAX_LENGTH: dict = {}


def log_same_line(msg: str, *args: Any) -> None:
    full_msg = msg % args
    if len(full_msg) > _LOG_MAX_LENGTH.get(None, 0):
        _LOG_MAX_LENGTH[None] = len(full_msg)

    max_length = _LOG_MAX_LENGTH[None]
    padding = max_length - len(full_msg)
    if padding > 0:
        full_msg = full_msg + " " * padding
    print(full_msg, end="\r")


def log_switch(logger: 'logging.Logger',
               debug: Callable,
               info: Callable) -> None:
    if logger.isEnabledFor(DEBUG):
        return debug()
    if logger.isEnabledFor(INFO):
        return info()
