import functools as _functools
import logging as _logging
import sqlite3 as _sqlite3

import hashdecoder.exc as _exceptions
import hashdecoder.lib.decoder as _decoder
import hashdecoder.lib.dictionary as _dictionary
import hashdecoder.lib.hashutil as _hashutil
import hashdecoder.lib.logutil as _logutil
import hashdecoder.lib.parse_args as _parse_args

log = _logging.getLogger(__name__)


def _configure_logging(verbosity: int) -> None:
    if verbosity > 1:
        _logging.basicConfig(level=_logging.DEBUG)
    elif verbosity > 0:
        _logging.basicConfig(level=_logging.INFO)
    else:
        _logging.basicConfig()
    log.debug("Log level set to: %s",
              _logging.getLevelName(log.getEffectiveLevel()))


def _get_dictionary(db: _sqlite3.Connection) -> '_dictionary.Dictionary':
    dictionary = _dictionary.get_db_dictionary(db)
    words = dictionary.count_initial_words()
    permutations = dictionary.count_permutations()
    log.debug(
        "Dictionary contains %s words, %s permutations, total %s entries",
        words, permutations, words + permutations)
    return dictionary


@_logutil.log_entry_and_exit(log.debug)
def process_db(dictionary, args: _parse_args.ParsedArgs) -> None:
    if args.db_cmd == _parse_args.DBCmdType.wipe.name:
        input("About to wipe database, press Enter to continue...")
        dictionary.clear()
        return

    if args.db_cmd == _parse_args.DBCmdType.count.name:
        words = dictionary.count_initial_words()
        permutations = dictionary.count_permutations()
        total = words + permutations
        print(
            "Dictionary contains {words} words, "
            "{permutations} permutations, "
            "total {total} entries".format(
                **locals())
        )
        return

    if args.db_cmd == _parse_args.DBCmdType.load.name:
        def add_word(index, word):
            _logutil.throttled_log(
                log.info, 'Adding %sth word: %s', index, word)
            dictionary.add_initial_word(word, args.hint)

        [add_word(i, w.strip())
         for i, w in enumerate(args.wordlist.readlines())]


@_logutil.log_entry_and_exit(log.debug)
def process_decode(dictionary, args: _parse_args.ParsedArgs) -> None:
    log.info('Initialising decoder')
    decoder = _decoder.HashDecoder(dictionary)

    log.info('Decoding hash %s', args.hash)
    decoded_hash = decoder.decode(args.hash, hint=args.hint)

    if args.quiet:
        print(decoded_hash)
    else:
        print("Decoded hash to: {}".format(decoded_hash))


@_logutil.log_entry_and_exit(log.debug)
def process_hash(args: _parse_args.ParsedArgs) -> None:
    print(_hashutil.md5_encode(args.word))


def main(args: _parse_args.ParsedArgs):
    db = _sqlite3.connect('db.sqlite')
    dictionary = _get_dictionary(db)
    try:
        _processors = {
            _parse_args.CmdType.db: _functools.partial(process_db, dictionary),
            _parse_args.CmdType.decode: _functools.partial(process_decode,
                                                           dictionary),
            _parse_args.CmdType.hash: process_hash,
        }
        cmd = _processors[_parse_args.CmdType[args.cmd]]
        cmd(args)
    except KeyboardInterrupt:
        print("Exiting")
        exit(2)
    except _exceptions.HashDecodeError as ex:
        print(ex)
        exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    vargs = _parse_args.parse_args()
    _configure_logging(vargs.verbosity)
    main(vargs)
