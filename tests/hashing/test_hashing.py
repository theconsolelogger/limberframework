from pytest import mark

from limberframework.hashing.hashers import Hasher


@mark.parametrize(
    "value,hashed_value",
    [
        ("test", "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"),
        (
            "https://127.0.0.1:5000|192.168.0.1",
            "abe9d8335021d0824fae8c13ea282e50b4f9b536",
        ),
    ],
)
def test_hash(value, hashed_value):
    hasher = Hasher("sha1")
    response = hasher.hash(value)

    assert response == hashed_value
