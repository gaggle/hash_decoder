import logging
import sqlite3
from argparse import ArgumentParser, FileType
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

from hashdecoder.exc import HashDecodeError
from hashdecoder.lib import logutil
from hashdecoder.lib.decoder import HashDecoder
from hashdecoder.lib.dictionary import DBDictionary
from hashdecoder.lib.fileutils import seek_at
from hashdecoder.lib.hashutil import md5_encode
from hashdecoder.lib.logutil import log_me, print_progress

if TYPE_CHECKING:
    from argparse import Namespace

log = logging.getLogger(__name__)

CmdType = Enum('CmdType', 'db decode hash')
DBCmdType = Enum('DBCmdType', 'count load wipe')


def _parse_args() -> 'Namespace':
    def add_flags(p: ArgumentParser, quiet: str = None) -> None:
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

    parser = ArgumentParser()

    cmds_parsers = parser.add_subparsers(dest='cmd')
    cmds_parsers.required = True  # type: ignore

    db_parser = cmds_parsers.add_parser(
        CmdType.db.name, help='database operations')
    db_cmds_parsers = db_parser.add_subparsers(dest='db_cmd')
    db_cmds_parsers.required = True  # type: ignore

    db_load_parser = db_cmds_parsers.add_parser(
        DBCmdType.load.name, help='append words to database')
    db_load_parser.add_argument(
        'wordlist', type=FileType('r'),
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


def _configure_logging(verbosity: int) -> None:
    if verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity > 0:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig()
    log.debug("Log level set to: %s",
              logging.getLevelName(log.getEffectiveLevel()))


def _get_dictionary() -> 'DBDictionary':
    dictionary = DBDictionary(db)
    words = dictionary.count_words()
    permutations = dictionary.count_permutations()
    log.info(
        "Dictionary contains %s words, %s permutations, total %s entries",
        words, permutations, words + permutations)
    return dictionary


@log_me
def process_db(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = _get_dictionary()

    if args.db_cmd == DBCmdType.wipe.name:
        input("About to wipe database, press Enter to continue...")
        dictionary.drop()
        return

    if args.db_cmd == DBCmdType.count.name:
        words = dictionary.count_words()
        permutations = dictionary.count_permutations()
        total = words + permutations
        print(
            "Dictionary contains {words} words, "
            "{permutations} permutations, "
            "total {total} entries".format(
                **locals())
        )
        return

    if args.db_cmd == DBCmdType.load.name:

        file = args.wordlist
        with seek_at(file, 0) as f:
            length = len(f.readlines())

        valid_chars = set(args.hint or [])
        valid_chars.remove(' ')

        def filtered_line_entries():
            for entry in file.readlines():
                if any((c in valid_chars) for c in entry):
                    yield entry

        print_progress(filtered_line_entries(),
                       dictionary.add_word,
                       length, prefix='Loading words')


@log_me
def process_decode(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = _get_dictionary()

    with log_ctx("Initialising decoder"):
        decoder = HashDecoder(dictionary)

    with log_ctx("Decoding hash %s", args.hash):
        decoded_hash = decoder.decode(args.hash, hint=args.hint)

    if args.quiet:
        print(decoded_hash)
    else:
        print("Decoded hash to: {}".format(decoded_hash))


@log_me
def process_hash(args: 'Namespace') -> None:
    print(md5_encode(args.word))


_processors = {
    CmdType.db: process_db,
    CmdType.decode: process_decode,
    CmdType.hash: process_hash,
}


def main(args):
    _configure_logging(args.verbosity)

    try:
        cmd = _processors[CmdType[args.cmd]]
        cmd(args)
    except KeyboardInterrupt as ex:
        print("Exiting")
        exit(2)
    except HashDecodeError as ex:
        print(ex)
        exit(1)


if __name__ == '__main__':
    vargs = _parse_args()

    log_ctx = partial(logutil.log_ctx, quiet=vargs.quiet,
                      verbose=vargs.verbosity)
    db = sqlite3.connect('db.sqlite')
    try:
        main(vargs)
    finally:
        db.close()
