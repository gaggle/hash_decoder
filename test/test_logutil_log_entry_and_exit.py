from logging import getLogger

from pytest import raises

from hashdecoder.lib.logutil import log_entry_and_exit


def test_normal_run(caplog):
    @log_entry_and_exit(getLogger("test").info)
    def foo():
        pass

    foo()
    ideal = """
logutil.py                  35 INFO     enter foo
logutil.py                  42 INFO     exit foo
""".lstrip()
    assert ideal == caplog.text


def test_exception_has_bespoke_msg(caplog):
    @log_entry_and_exit(getLogger("test").info)
    def foo():
        raise Exception("Break!")

    with raises(Exception):
        foo()

    ideal = """
logutil.py                  35 INFO     enter foo
logutil.py                  39 INFO     exit foo with error: Break!
""".lstrip()
    assert ideal == caplog.text
