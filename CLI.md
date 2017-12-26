    $ python -m hashdecoder --help

    usage: __main__.py [-h] {db,decode,hash} ...
    
    positional arguments:
      {db,decode,hash}
        db              database operations
        decode          decode a hash
        hash            hash a word
    
    optional arguments:
      -h, --help        show this help message and exit

---

    $ python -m hashdecoder db --help

    usage: __main__.py db [-h] {load,count,wipe} ...
    
    positional arguments:
      {load,count,wipe}
        load             append words to database
        count            display number of entries in database
        wipe             wipe words in database
    
    optional arguments:
      -h, --help         show this help message and exit

---

    $ python -m hashdecoder decode --help

    usage: __main__.py decode [-h] [--hint HINT [HINT ...]] [-quiet] [-v] hash
    
    positional arguments:
      hash                  hash to decode
    
    optional arguments:
      -h, --help            show this help message and exit
      --hint HINT [HINT ...]
                            anagram of solution, to speed up computations
      -quiet, --quiet       only output decoded hash
      -v, --verbosity       increase output verbosity

---

    $ python -m hashdecoder hash --help

    usage: __main__.py hash [-h] [-v] word [word ...]
    
    positional arguments:
      word             word to hash
    
    optional arguments:
      -h, --help       show this help message and exit
      -v, --verbosity  increase output verbosity
