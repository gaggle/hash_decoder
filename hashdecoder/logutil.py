from contextlib import contextmanager
from typing import Any, Iterator


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
        try:
            yield
        except Exception:
            print("ERROR")
            raise
        else:
            print('OK')
