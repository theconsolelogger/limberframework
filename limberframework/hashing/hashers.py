"""Hashers for hashing data."""
import hashlib


class Hasher:
    """Hashes data using a specified algorithm.

    Attributes:
        algorithm: Name of a hash algorithm.
    """

    def __init__(self, algorithm: str) -> None:
        """Establish the algorithm.

        Args:
            algorithm: Name of a hash algorithm.
        """
        self.algorithm = algorithm

    def __call__(self, value: str) -> str:
        """Hashes a string using the sha1 algorithm.

        Args:
            value: String to hash.

        Returns:
            str: String representation of hashed value.
        """
        encoded_value = value.encode()
        hasher = hashlib.new(self.algorithm)
        hasher.update(encoded_value)
        return hasher.hexdigest()
