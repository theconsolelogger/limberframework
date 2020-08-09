from datetime import datetime, timedelta
from os import getcwd
from unittest.mock import patch
from pytest import raises, mark
from limberframework.cache.stores import make_store, FileStore

def test_make_store_file_store():
    config = {
        'driver': 'file'
    }
    base_path = getcwd()

    response = make_store(config, base_path=base_path)

    assert isinstance(response, FileStore)
    assert response.directory == base_path

def test_make_store_invalid_driver():
    config = {
        'driver': 'test'
    }

    with raises(ValueError) as excinfo:
        make_store(config)

    assert f"Unsupported cache driver {config['driver']}." in str(excinfo.value)

@mark.parametrize('directory,path', [
    ('/test','/test/a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'),
    ('/Users/test/projects/limber/storage/cache', '/Users/test/projects/limber/storage/cache/a94a8fe5ccb19ba61c4c0873d391e987982fbbd3')
])
def test_file_store_path(directory, path):
    key = 'test'

    file_store = FileStore(directory)
    response = file_store.path(key)

    assert response == path

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_get(mock_file_system):
    date = datetime.now() + timedelta(seconds=60)
    value = 'test'
    content = date.isoformat() + ',' + value
    mock_file_system.read_file.return_value = content

    file_store = FileStore('/test')
    response = file_store.get('test')

    assert response == {
        'data': value,
        'expires_at': date
    }

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_get_expired(mock_file_system):
    date = datetime.now() - timedelta(seconds=60)
    value = 'test'
    content = date.isoformat() + ',' + value
    mock_file_system.read_file.return_value = content

    file_store = FileStore('/test')
    response = file_store.get('test')

    assert response == {
        'data': None,
        'expires_at': None
    }

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_get_invalid_file(mock_file_system):
    mock_file_system.read_file.side_effect = FileNotFoundError()

    file_store = FileStore('/test')
    response = file_store.get('test')

    assert response == {
        'data': None,
        'expires_at': None
    }

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_put(mock_file_system):
    key = 'test'
    value = 'test'
    expires_at = datetime.now()

    file_store = FileStore('/test')
    response = file_store.put(key, value, expires_at)

    assert response
    mock_file_system.write_file.assert_called_once()

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_add_invalid_file(mock_file_system):
    mock_file_system.has_file.return_value = False
    key = 'test'
    value = 'test'
    expires_at = datetime.now()

    file_store = FileStore('/test')
    response = file_store.add(key, value, expires_at)

    assert response == False

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_add(mock_file_system):
    mock_file_system.has_file.return_value = True
    key = 'test'
    value = 'test'
    expires_at = datetime.now()

    file_store = FileStore('/test')
    response = file_store.add(key, value, expires_at)

    assert response

@patch('limberframework.cache.stores.FileSystem')
def test_file_store_get_item(mock_file_system):
    date = datetime.now() - timedelta(seconds=60)
    value = 'test'
    content = date.isoformat() + ',' + value
    mock_file_system.read_file.return_value = content

    file_store = FileStore('/test')
    response = file_store['test']

    assert response == {
        'data': None,
        'expires_at': None
    }
