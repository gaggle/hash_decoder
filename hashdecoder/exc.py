class HashDecodeError(Exception):
    def __init__(self, hash_: str) -> None:
        super().__init__("Could not decode {}".format(hash_))
