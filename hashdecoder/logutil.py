from contextlib import contextmanager


@contextmanager
def log_ctx(msg, *args, quiet=False, verbose=False):
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
