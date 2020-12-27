"""Handles interacting with files and directories."""
from os import remove
from os.path import isfile


class FileSystem:
    """Performs actions on files and directories."""

    @staticmethod
    def has_file(path: str) -> bool:
        """Check if a file exists at the system path.

        Args:
            path: System path to file.

        Returns bool.
        """
        if isfile(path):
            return True
        return False

    @staticmethod
    def read_file(path: str) -> str:
        """Retrieve the contents of a file from storage.

        Args:
            path: System path to file.

        Returns:
            str: Contents of the file.

        Raises:
            FileNotFoundError: If the path does not contain a file.
        """
        if not isfile(path):
            raise FileNotFoundError(f"File does not exist at path {path}.")

        with open(path, "r") as reader:
            file_contents = reader.read()

        return file_contents

    @staticmethod
    def write_file(path: str, contents: str) -> None:
        """Write a file to the system.

        Args:
            path: System path to file.
            contents: Contents to write to the file.
        """
        with open(path, "w") as writer:
            writer.write(contents)

    @staticmethod
    def remove(path: str) -> bool:
        """Remove file from cache.

        Args:
            path: System path to file.

        Returns:
            bool: False if file not found, true if removed.
        """
        if not isfile(path):
            return False

        remove(path)
        return True
