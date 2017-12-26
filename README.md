# hash decoder
[![Build Status](https://travis-ci.org/gaggle/hash_decoder.svg?branch=master)](https://travis-ci.org/gaggle/hash_decoder)
[![Test Coverage](https://api.codeclimate.com/v1/badges/a38a3b93be1611bb6a76/test_coverage)](https://codeclimate.com/github/gaggle/hash_decoder/test_coverage)
[![Known Vulnerabilities](https://snyk.io/test/github/gaggle/hash_decoder/badge.svg)](https://snyk.io/test/github/gaggle/hash_decoder)

Simple hash decoder experiment

Use the `--hint` option to reduce the search-space. 

E.g. if you're looking to break the hash `e4820b45d2277f3844eac66c903e84be`, 
and you know the anagram of the decoded phrase is "poultry outwits ants", 
it will be **significantly** quicker to let the system consume that hint.

See [CLI.md](CLI.md) for usage details.
