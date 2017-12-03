import functools
from contextlib import contextmanager
from inspect import currentframe, getouterframes
from logging import DEBUG, INFO, getLogger
from shutil import get_terminal_size
from sys import stdout
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
        stdout.flush()
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


AUTO = ''


def print_progress(content: Iterator, apply_to: Callable, end_val: int,
                   prefix='Percent', bar_length: int = AUTO):
    max_length = 0
    max_allowed_length = 40

    if bar_length is AUTO:
        width, height = get_terminal_size((80, 20))
        bar_length = width - (len(prefix) + max_allowed_length)

    def to_display(el):
        nonlocal max_length
        el_for_print = el.replace('\n', '')

        if len(el) > max_allowed_length:
            el = el[:max_allowed_length]

        if len(el) > max_length:
            max_length = len(el)
        padding = max_length - len(el)
        if padding > 0:
            el_for_print = el_for_print + ' ' * padding
        return el_for_print

    def calc_percentage_bar():
        percent_ = float(i) / end_val
        raw_hashes = '#' * int(round(percent_ * bar_length))
        hashes_ = raw_hashes + ' ' * (bar_length - len(raw_hashes))
        percent_ = int(round(percent_ * 100))
        return hashes_, percent_

    for i, e in enumerate(content):
        apply_to(e)
        element = to_display(e)
        hashes, percent = calc_percentage_bar()
        print(
            "\r{prefix}: [{hashes}] "
            "{percent}%: {element}".format(**locals()),
            end=''
        )
    print('')


def whoami():
    return getouterframes(currentframe())[1].function


def log_me(inner):
    @functools.wraps(inner)
    def wrapped(*args, **kwargs):
        log.debug('enter %s', inner.__name__)
        try:
            r = inner(*args, **kwargs)
        finally:
            log.debug('exit %s', inner.__name__)
        return r

    return wrapped
