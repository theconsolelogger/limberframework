"""Filesystem

Classes:
- Filesystem: handles interacting with files and directories.
"""
from os import remove
from os.path import isfile

class FileSystem:
    """Performs actions on files and directories."""
    @staticmethod
    def has_file(path: str) -> bool:
        """Checks if a file exists at the system path.

        Arguments:
        path str -- system path to file.

        Returns bool.
        """
        if isfile(path):
            return True
        return False

    @staticmethod
    def read_file(path: str) -> str:
        """Retrieves the contents of a file from storage.

        Arguments:
        path str -- system path to file.

        Returns:
        str -- contents of the file.
        """
        if not isfile(path):
            raise FileNotFoundError(f'File does not exist at path {path}.')

        with open(path, 'r') as reader:
            file_contents = reader.read()

        return file_contents

    @staticmethod
    def write_file(path: str, contents: str) -> None:
        """Writes a file to the system.

        Arguments:
        path str -- system path to file.
        contents: str -- contents to write to the file.
        """
        with open(path, 'w') as writer:
            writer.write(contents)

    @staticmethod
    def remove(path: str) -> bool:
        """Remove file from cache.

        Arguments:
        path str -- system path to file.

        Returns:
        bool -- false if file not found, true if removed.
        """
        if not isfile(path):
            return False

        remove(path)
        return True
