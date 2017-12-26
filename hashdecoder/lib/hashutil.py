from hashlib import md5


def md5_encode(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()
