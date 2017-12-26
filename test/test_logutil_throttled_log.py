from logging import getLogger

from hashdecoder.lib.logutil import throttled_log


def test_called_twice_only_logs_once(caplog):
    log = getLogger("test").info
    throttled_log(log, "msg %s", "1")
    throttled_log(log, "msg %s", "2")
    ideal = "logutil.py                  53 INFO     msg 1\n"
    assert ideal == caplog.text
