"""Hashers

Classes:
- Hahser: handles hashing data.
"""
import hashlib

class Hasher:
    """Hashes data using a specified algorithm.

    Attributes:
    algorithm str -- name of a hash algorithm.
    """
    def __init__(self, algorithm: str) -> None:
        """Establishes the hasher.

        Arguments:
        algorithm str -- name of a hash algorithm.
        """
        self.algorithm = algorithm

    def hash(self, value: str) -> str:
        """Hashes a string using the sha1 algorithm.

        Arguments:
        value str -- string to hash.

        Returns:
        str -- string representation of hashed value.
        """
        encoded_value = value.encode()
        hasher = hashlib.new(self.algorithm)
        hasher.update(encoded_value)
        return hasher.hexdigest()
