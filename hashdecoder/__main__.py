import logging
import sqlite3
from argparse import ArgumentParser, FileType
from enum import Enum
from functools import partial
from hashlib import md5
from typing import TYPE_CHECKING

from hashdecoder.decoder import HashDecoder
from hashdecoder.dictionary import DBDictionary
from hashdecoder.lib import logutil
from hashdecoder.lib.word_repository import FilePathWordRepository

if TYPE_CHECKING:
    from argparse import Namespace

log = logging.getLogger(__name__)

CmdType = Enum('CmdType', 'init decode hash')


def _parse_args() -> 'Namespace':
    def add_flags(p, q=None):
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

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    init_parser = subparsers.add_parser(
        CmdType.init.name, help='initialise database from list of words')
    init_parser.add_argument(
        'wordlist', type=FileType('r'),
        help='path to new-line delimited list of words')
    add_flags(init_parser)

    decode_parser = subparsers.add_parser(
        CmdType.decode.name, help='decode a hash')
    decode_parser.add_argument('hash', type=str, help='hash to decode')
    add_flags(decode_parser, "only output decoded hash")

    hash_parser = subparsers.add_parser(
        CmdType.hash.name, help='hash a word')

    hash_parser.add_argument('word', type=str, help='word to hash', nargs='+')
    add_flags(hash_parser)

    args = parser.parse_args()

    if not hasattr(args, 'quiet'):
        setattr(args, 'quiet', False)
    if not hasattr(args, 'verbosity'):
        setattr(args, 'verbosity', 0)
    return args


def _configure_logging(verbosity):
    if verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity > 0:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig()
    log.debug("Log level set to: %s",
              logging.getLevelName(log.getEffectiveLevel()))


def process_init(args) -> None:
    print(args)


def process_decode(args: 'Namespace') -> None:
    with log_ctx("Loading dictionary"):
        dictionary = DBDictionary(db)
        log.info("Dictionary contains %s words", dictionary.count())

    if args.wordlist:
        with log_ctx("Adding data from %s", args.wordlist):
            for word in FilePathWordRepository(
                    args.wordlist).yield_words():
                dictionary.add_word(word)

    with log_ctx("Initialising decoder"):
        decoder = HashDecoder(dictionary)

    with log_ctx("Decoding hash %s", args.hash):
        decoded_hash = decoder.decode(args.hash)

    if args.quiet:
        print(decoded_hash)
    else:
        print("Decoded hash {} to: {}".format(args.hash, decoded_hash))


def process_hash(args) -> None:
    msg = ' '.join(args.word)
    print(md5(msg.encode('utf-8')).hexdigest())


_processors = {
    CmdType.init: process_init,
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
        cmd = _processors[CmdType[vargs.cmd]]
        cmd(vargs)
    except KeyboardInterrupt as ex:
        print("Quit")
        exit(1)
    finally:
        db.close()
