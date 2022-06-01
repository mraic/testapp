import os

import pytest
from src import create_app


@pytest.fixture(scope='session')
def app(request):
    flask_app = create_app(os.environ.get('FLASK_ENV', 'development'))

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return flask_app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "run: mark test to run only on named environment"
    )
