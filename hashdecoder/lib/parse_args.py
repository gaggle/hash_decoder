import argparse as _argparse
import enum as _enum
import logging as _logging
from collections import namedtuple
from typing import NewType

log = _logging.getLogger(__name__)

CmdType = _enum.Enum('CmdType', 'db decode hash')
DBCmdType = _enum.Enum('DBCmdType', 'count load wipe')
ParsedArgs = NewType('ParsedArgs', namedtuple('ParsedArgs', [
    'cmd',
    'db_cmd',
    'hash',
    'hint',
    'quiet',
    'verbosity',
    'word',
    'wordlist',
]))


def parse_args() -> ParsedArgs:
    def add_flags(p: _argparse.ArgumentParser, quiet: str = None) -> None:
        if quiet:
            p.add_argument(
                "-quiet", "--quiet",
                action="store_true",
                help=quiet,
            )

        p.add_argument(
            '-v', '--verbosity',
            action="count",
            default=0,
            help="increase output verbosity",
        )

    parser = _argparse.ArgumentParser()

    cmds_parsers = parser.add_subparsers(dest='cmd')
    cmds_parsers.required = True  # type: ignore

    db_parser = cmds_parsers.add_parser(
        CmdType.db.name, help='database operations')
    db_cmds_parsers = db_parser.add_subparsers(dest='db_cmd')
    db_cmds_parsers.required = True  # type: ignore

    db_load_parser = db_cmds_parsers.add_parser(
        DBCmdType.load.name, help='append words to database')
    db_load_parser.add_argument(
        'wordlist', type=_argparse.FileType('r'),
        help='path to new-line delimited list of words')
    db_load_parser.add_argument(
        '--hint', type=str, nargs='+',
        help='anagram of solution, to speed up computations'
    )
    add_flags(db_load_parser)

    db_count_parser = db_cmds_parsers.add_parser(
        DBCmdType.count.name, help='display number of entries in database')
    add_flags(db_count_parser)

    db_wipe_parser = db_cmds_parsers.add_parser(
        DBCmdType.wipe.name, help='wipe words in database')
    add_flags(db_wipe_parser)

    decode_parser = cmds_parsers.add_parser(
        CmdType.decode.name, help='decode a hash')
    decode_parser.add_argument('hash', type=str, help='hash to decode')
    decode_parser.add_argument(
        '--hint', type=str, nargs='+',
        help='anagram of solution, to speed up computations'
    )
    add_flags(decode_parser, quiet="only output decoded hash")

    hash_parser = cmds_parsers.add_parser(
        CmdType.hash.name, help='hash a word')

    hash_parser.add_argument('word', type=str, help='word to hash', nargs='+')
    add_flags(hash_parser)

    args = parser.parse_args()

    if not hasattr(args, 'quiet'):
        setattr(args, 'quiet', False)
    if not hasattr(args, 'verbosity'):
        setattr(args, 'verbosity', 0)
    if hasattr(args, 'hint') and args.hint:
        args.hint = ' '.join(args.hint)
    if hasattr(args, 'word'):
        args.word = ' '.join(args.word)
    return args
