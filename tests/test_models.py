from unittest.mock import Mock
from pytest import fixture
from limberframework.database.models import Model

@fixture
def model():
    return Model()

@fixture
def session():
    return Mock()

def test_create_model(model):
    assert model.soft_delete == False
    assert model.__tablename__ == 'model'

def test_first(model, session):
    model.first(session)

    session.query.assert_called_with(Model)
    session.query.return_value.first.assert_called_once()

def test_get(model, session):
    id = 1
    model.get(session, id)

    session.query.assert_called_with(Model)
    session.query.return_value.get.assert_called_with(id)

def test_filter(model, session):
    id = 1
    model.filter(session, id=id)

    session.query.assert_called_with(Model)
    session.query.return_value.filter_by.assert_called_with(id=id)
    session.query.return_value.filter_by.return_value.all.assert_called_once()

def test_create(model, session):
    attributes = {
        'soft_delete': True
    }

    response = model.create(session, attributes)

    for attribute, value in attributes.items():
        assert getattr(response, attribute) == value

def test_save(model, session):
    response = model.save(session)

    session.add.assert_called_with(model)
    assert response == model

def test_update(model):
    attributes = {
        'id': 1,
        'soft_delete': True
    }

    response = model.update(attributes)

    assert response == model

    for attribute, value in attributes.items():
        assert getattr(model, attribute) == value

def test_destroy(model, session):
    response = model.destroy(session)

    assert response == None
    session.delete.assert_called_with(model)
