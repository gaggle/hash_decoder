from io import TextIOWrapper

from pytest import raises

from hashdecoder.lib.parse_args import parse_args


def test_empty_raises(capfd):
    with raises(SystemExit):
        parse_args([])
    out, err = capfd.readouterr()
    assert not out
    assert err


def test_db_count():
    args = parse_args(['db', 'count'])
    assert 'db' == args.cmd
    assert 'count' == args.db_cmd
    assert 0 == args.verbosity


def test_db_load():
    args = parse_args(['db', 'load', __file__, '-v', '--hint', 'foo bar'])
    assert 'db' == args.cmd
    assert 'load' == args.db_cmd
    assert isinstance(args.wordlist, TextIOWrapper)
    assert 1 == args.verbosity
    assert 'foo bar' == args.hint


def test_db_wipe():
    args = parse_args(['db', 'wipe', '-vv'])
    assert 'db' == args.cmd
    assert 'wipe' == args.db_cmd
    assert 2 == args.verbosity


def test_decode():
    args = parse_args(['decode', '1234', '--hint', 'foo bar', '-q'])
    assert 'decode' == args.cmd
    assert '1234' == args.hash
    assert 'foo bar' == args.hint
    assert True is args.quiet


def test_hash():
    args = parse_args(['hash', 'foo bar'])
    assert 'hash' == args.cmd
    assert 'foo bar' == args.word
