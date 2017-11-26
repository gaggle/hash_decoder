import logging
from argparse import ArgumentError, ArgumentParser
from functools import partial
from os import path

from hashdecoder import logutil

log = logging.getLogger(__name__)


def _parse_args():
    def wordlist(value):
        abspath = path.abspath(value)
        if not path.isfile(abspath):
            raise ArgumentError("Not a valid file")
        return abspath

    parser = ArgumentParser()
    parser.add_argument("hash", help="hash to decode")
    parser.add_argument(
        "-w", "--wordlist",
        default="wordlist.dms",
        help="path to new-line delimited list of word list",
        type=wordlist,
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="only display decoded hash",
    )
    parser.add_argument(
        '-v', '--verbosity',
        action="count",
        default=0,
        help="increase output verbosity",
    )
    return parser.parse_args()


vargs = _parse_args()

log_ctx = partial(logutil.log_ctx, quiet=vargs.quiet, verbose=vargs.verbosity)

if vargs.verbosity > 1:
    logging.basicConfig(level=logging.DEBUG)
elif vargs.verbosity > 0:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig()

log.debug("Log level set to: %s",
          logging.getLevelName(log.getEffectiveLevel()))

with log_ctx("Initialising decoder"):
    pass

with log_ctx("Decoding hash %s", vargs.hash):
    decoded_hash = 'not-implemented'

if vargs.quiet:
    print(decoded_hash)
else:
    print("Decoded hash {} to: {}".format(vargs.hash, decoded_hash))
