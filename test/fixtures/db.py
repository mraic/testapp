from unittest.mock import MagicMock
import pytest


@pytest.fixture(scope='session')
def db(app):
    from src import db as _db

    _db.session = MagicMock()
    return _db
