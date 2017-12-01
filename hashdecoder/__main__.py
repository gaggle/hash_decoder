import logging
import sqlite3
from argparse import ArgumentParser, FileType
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

from hashdecoder.decoder import HashDecoder
from hashdecoder.dictionary import DBDictionary
from hashdecoder.lib import logutil

if TYPE_CHECKING:
    from hashdecoder.dictionary import Dictionary
    from argparse import Namespace

log = logging.getLogger(__name__)

CmdType = Enum('CmdType', 'db decode hash')


def _parse_args() -> 'Namespace':
    def add_flags(p: ArgumentParser, q: str = None) -> None:
        if q:
            p.add_argument(
                "-q", "--quiet",
                action="store_true",
                help=q,
            )

        p.add_argument(
            '-v', '--verbosity',
            action="count",
            default=0,
            help="increase output verbosity",
        )

    parser = ArgumentParser()

    cmds_parsers = parser.add_subparsers(dest='cmd')
    cmds_parsers.required = True

    db_parser = cmds_parsers.add_parser(
        CmdType.db.name, help='database operations')
    db_cmds_parsers = db_parser.add_subparsers(dest='db_cmd')
    db_cmds_parsers.required = True

    db_load_parser = db_cmds_parsers.add_parser(
        'load', help='append words to database')
    db_load_parser.add_argument(
        'wordlist', type=FileType('r'),
        help='path to new-line delimited list of words')
    add_flags(db_load_parser)

    db_count_parser = db_cmds_parsers.add_parser(
        'count', help='display number of entries in database')
    add_flags(db_count_parser)

    db_wipe_parser = db_cmds_parsers.add_parser(
        'wipe', help='wipe words in database')
    add_flags(db_wipe_parser)

    decode_parser = cmds_parsers.add_parser(
        CmdType.decode.name, help='decode a hash')
    decode_parser.add_argument('hash', type=str, help='hash to decode')
    add_flags(decode_parser, "only output decoded hash")

    hash_parser = cmds_parsers.add_parser(
        CmdType.hash.name, help='hash a word')

    hash_parser.add_argument('word', type=str, help='word to hash', nargs='+')
    add_flags(hash_parser)

    args = parser.parse_args()

    if not hasattr(args, 'quiet'):
        setattr(args, 'quiet', False)
    if not hasattr(args, 'verbosity'):
        setattr(args, 'verbosity', 0)
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


def _get_dictionary() -> 'Dictionary':
    dictionary = DBDictionary(db)
    words = dictionary.count_words()
    permutations = dictionary.count_permutations()
    log.info(
        "Dictionary contains %s words, %s permutations, total %s entries",
        words, permutations, words + permutations)
    return dictionary


def process_db(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = _get_dictionary()

    if args.db_cmd == 'wipe':
        input("Wiping database, press Enter to continue...")
        db.executescript('drop table if exists words')
        return

    if args.db_cmd == 'count':
        print("{} entries".format(dictionary.count()))
        return

    with log_ctx("Adding data from %s", args.wordlist.name):
        for word in args.wordlist:
            print(word)
            # for word in BufferWordRepository(args.wordlist).yield_words():
            #     dictionary.add_word(word)


def process_decode(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = _get_dictionary()

    with log_ctx("Initialising decoder"):
        decoder = HashDecoder(dictionary)

    with log_ctx("Decoding hash %s", args.hash):
        decoded_hash = decoder.decode(args.hash)

    if args.quiet:
        print(decoded_hash)
    else:
        print("Decoded hash {} to: {}".format(args.hash, decoded_hash))


def process_hash(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = _get_dictionary()

    word = ' '.join(args.word)
    if not dictionary.lookup_hash(word):
        dictionary.add_permutation(word)
    print(dictionary.lookup_hash(word))


_processors = {
    CmdType.db: process_db,
    CmdType.decode: process_decode,
    CmdType.hash: process_hash,
}

if __name__ == '__main__':
    vargs = _parse_args()
    log_ctx = partial(logutil.log_ctx, quiet=vargs.quiet,
                      verbose=vargs.verbosity)
    _configure_logging(vargs.verbosity)

    db = sqlite3.connect('db.sqlite')
    try:
        _get_dictionary()
        cmd = _processors[CmdType[vargs.cmd]]
        cmd(vargs)
    except KeyboardInterrupt as ex:
        print("Exiting")
        exit(1)
    finally:
        db.close()
