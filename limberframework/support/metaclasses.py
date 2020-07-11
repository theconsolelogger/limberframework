"""Metaclasses

Custom metaclasses to control the
creation of instances of a class.

Classes:
- Singleton: restricts classes to a single instance.
"""
class Singleton(type):
    """Metaclass that restricts the instanciation of a class
    to one single instance.

    Attributes:
    - _instances Dict -- instances of singleton classes.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Controls the creation of a class, returning
        an existing instance if available.

        Arguments:
        - cls Singleton -- a class with the metaclass set to Singleton.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
