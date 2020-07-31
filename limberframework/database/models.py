"""Models

Classes:
- Model: base class for declarative class definitions.
"""
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

@as_declarative()
class Model:
    """Base class for declarative class definitions."""
    id: Any
    __name__: str
    soft_delete: bool = False

    @declared_attr
    def __tablename__(cls) -> str:
        """Sets the name of the database table to
        the class name in lowercase.
        """
        return cls.__name__.lower()

    @classmethod
    def check_soft_deletes(cls, query: Query) -> Query:
        """Adds filter for deleted_at column
        if Model is set as soft deletes.

        Arguments:
        query Query -- query to add filter.

        Returns:
        Query -- with or without deleted_at filter.
        """
        if cls.soft_delete:
            query.filter_by(deleted_at=None)
        return query

    @classmethod
    def all(cls, database: Session) -> List[Dict]:
        """Returns all records in the database table.

        Arguments:
        database Session -- Session object.

        Returns:
        list -- list of records.
        """
        return cls.check_soft_deletes(database.query(cls)).all()

    @classmethod
    def first(cls, database: Session) -> Dict:
        """Returns the first record in the database table.

        Arguments:
        database Session -- Session object.

        Returns:
        dict -- dict containing the first record.
        """
        return cls.check_soft_deletes(database.query(cls)).first()

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
        return cls.check_soft_deletes(database.query(cls)).get(id)

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
        return cls.check_soft_deletes(database.query(cls)).filter_by(**kwargs).all()

    @classmethod
    def create(cls, session: Session, attributes: Dict, **kwargs) -> 'Model':
        """Creates a new instance of the model and adds to a database session.

        Arguments:
        database Session -- Session object.
        attributes Dict -- attributes to set on the model.

        Returns:
        Model -- a new instance of Model with stated attributes.
        """
        model_object = cls(**attributes, **kwargs)
        return model_object.save(session)

    def save(self, session: Session) -> 'Model':
        """Adds a Model to a database session.

        Arguments:
        session Session -- Session object to add model too.

        Returns:
        Model -- the current Model instance.
        """
        session.add(self)
        return self

    def update(self, attributes: Dict) -> 'Model':
        """Changes the attributes of the Model.

        Arguments:
        attributes Dict -- attributes to change with values.

        Returns:
        Model -- the current Model instance.
        """
        for attribute, value in attributes.items():
            setattr(self, attribute, value)
        return self

    def destroy(self, session: Session) -> None:
        """Removes the Model in a database session.

        Arguments:
        session Session -- Session object to remove the model from.
        """
        if self.soft_delete:
            self.update({'deleted_at': datetime.now()})
        else:
            session.delete(self)
