from os import getcwd, remove
from os.path import isfile
from pytest import fixture, raises, mark
from limberframework.filesystem.filesystem import FileSystem

document_path = getcwd() + '/tests/test_file.py'
document_content = 'test'

@fixture
def document():
    with open(document_path, 'w') as writer:
        writer.write(document_content)

    yield

    try:
        remove(document_path)
    except Exception:
        pass

@mark.parametrize('path,exists', [
    (document_path, True),
    (getcwd() + '/tests/tests.py', False)
])
def test_has_file(path, exists, document):
    response = FileSystem.has_file(path)
    assert response == exists

def test_read_file(document):
    response = FileSystem.read_file(document_path)
    assert response == document_content

def test_read_file_execption():
    with raises(FileNotFoundError) as execinfo:
        FileSystem.read_file(document_path)

    assert f"File does not exist at path {document_path}" in str(execinfo.value)

def test_write_file():
    FileSystem.write_file(document_path, document_content)
    assert isfile(document_path)

    with open(document_path, 'r') as reader:
        content = reader.read()
    
    assert content == document_content

@mark.parametrize('path,removed', [
    (document_path, True),
    (getcwd() + '/tests/tests.py', False)
])
def test_remove(path, removed, document):
    response = FileSystem.remove(path)
    assert response == removed
