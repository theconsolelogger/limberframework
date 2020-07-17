"""Models

Classes:
- Model: base class for declarative class definitions.
"""
from typing import Any, Dict, List
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

@as_declarative()
class Model:
    """Base class for declarative class definitions."""
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Sets the name of the database table to
        the class name in lowercase.
        """
        return cls.__name__.lower()

    @classmethod
    def all(cls, database: Session) -> List[Dict]:
        """Returns all records in the database table.

        Arguments:
        database Session -- Session object.

        Returns:
        list -- list of records.
        """
        return database.query(cls).all()

    @classmethod
    def first(cls, database: Session) -> Dict:
        """Returns the first record in the database table.

        Arguments:
        database Session -- Session object.

        Returns:
        dict -- dict containing the first record.
        """
        return database.query(cls).first()

    @classmethod
    def get(cls, database: Session, id: int) -> Dict:
        """Returns the record in the database
        table with the stated primary key.

        Arguments:
        database Session -- Session object.
        id int -- primary key of the record.

        Returns:
        dict -- dict containing the first record.
        """
        return database.query(cls).get(id)

    @classmethod
    def filter(cls, database: Session, **kwargs) -> List:
        """Returns the records in the database
        table that match the stated criteria.

        Arguments:
        database Session -- Session object.
        **kwargs -- criteria used for filtering.

        Returns:
        list -- list of records.
        """
        return database.query(cls).filter_by(**kwargs).all()
