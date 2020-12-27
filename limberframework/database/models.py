"""Base class for declarative class definitions."""
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query


@as_declarative()
class Model:
    """Base class for declarative class definitions.

    Attributes:
        id: ID of the model.
        __name__: Name of the model.
        soft_delete: Whether the model is removed from the database.
    """

    id: Any
    __name__: str
    soft_delete: bool = False

    @declared_attr
    def __tablename__(cls) -> str:
        """Set the name of the database table.

        Sets the database table name to the class name in lowercase.
        """
        return cls.__name__.lower()

    @classmethod
    def check_soft_deletes(cls, query: Query) -> Query:
        """Add filter for deleted_at column if Model is set as soft deletes.

        Args:
            query: Query to add filter.

        Returns:
            Query: With or without deleted_at filter.
        """
        if cls.soft_delete:
            query.filter_by(deleted_at=None)
        return query

    @classmethod
    def all(cls, database: Session) -> List[Dict]:
        """Return all records in the database table.

        Args:
            database: Session to use to query the database.

        Returns:
            list: List of records retrieved from the database query.
        """
        return cls.check_soft_deletes(database.query(cls)).all()

    @classmethod
    def first(cls, database: Session) -> Dict:
        """Return the first record in the database table.

        Args:
            database: Session to use to query the database.

        Returns:
            dict: Dict containing the first record.
        """
        return cls.check_soft_deletes(database.query(cls)).first()

    @classmethod
    def get(cls, database: Session, id: int) -> Dict:
        """Return the record in the database table with the stated primary key.

        Args:
            database: Session to use to query the database.
            id: Primary key of the record.

        Returns:
            dict: Dict containing the first record.
        """
        return cls.check_soft_deletes(database.query(cls)).get(id)

    @classmethod
    def filter(cls, database: Session, **kwargs) -> List:
        """Return the records in the database table that match the stated criteria.

        Args:
            database: Session to use to query the database.
            **kwargs: criteria used for filtering.

        Returns:
            list: List of records retrieved from the database query.
        """
        return (
            cls.check_soft_deletes(database.query(cls))
            .filter_by(**kwargs)
            .all()
        )

    @classmethod
    def create(cls, session: Session, attributes: Dict, **kwargs) -> "Model":
        """Create a new instance of the model and adds to a database session.

        Args:
            database: Session to use to query the database.
            attributes: Attributes to set on the model.

        Returns:
            Model: A new instance of Model with stated attributes.
        """
        model_object = cls(**attributes, **kwargs)
        return model_object.save(session)

    def save(self, session: Session) -> "Model":
        """Add a Model to a database session.

        Args:
            session: Session to use to query the database.

        Returns:
            Model: The current Model instance.
        """
        session.add(self)
        return self

    def update(self, attributes: Dict) -> "Model":
        """Change the attributes of the Model.

        Args:
            attributes: Attributes to change with values.

        Returns:
            Model: The current Model instance.
        """
        for attribute, value in attributes.items():
            setattr(self, attribute, value)
        return self

    def destroy(self, session: Session) -> None:
        """Remove the Model in a database session.

        Args:
            session: Session to use to query the database.
        """
        if self.soft_delete:
            self.update({"deleted_at": datetime.now()})
        else:
            session.delete(self)
