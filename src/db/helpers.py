import contextlib
import urllib

import sqlalchemy as sa
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def truncate_db(db):
    with db.engine.connect() as con:
        con.execution_options(autocommit=True).execute(
            f"TRUNCATE TABLE {','.join(sorted_tables(db))}"
        )


def sorted_tables(db):
    return [_.name for _ in db.metadata.sorted_tables]


def create_db(app, tablespace_name):
    db = app.extensions["sqlalchemy"].db
    with _system_engine(app) as engine:
        engine.execute(
            f"""
                CREATE DATABASE {db.engine.url.database}
                WITH ENCODING='UTF8' OWNER={db.engine.url.username}
                CONNECTION LIMIT=-1 TABLESPACE={tablespace_name};
            """
        )


def create_tablespace(app, name, location="/data_tmpfs/postgresql"):
    with _system_engine(app) as engine:
        _create_tablespace(engine, name, location)


def drop_tablespace(app, name):
    with _system_engine(app) as engine:
        _drop_tablespace(engine, name)


def recreate_tablespace(app, name, location):
    with _system_engine(app) as engine:
        _drop_tablespace(engine, name)
        _create_tablespace(engine, name, location)


def _create_tablespace(engine, name, location="/data_tmpfs/postgresql"):
    engine.execute(f"CREATE TABLESPACE {name} LOCATION '{location}';")


def _drop_tablespace(engine, name):
    if (
        _get_scalar_result(
            engine,
            f"SELECT count(*) from pg_catalog.pg_tablespace WHERE spcname = '{name}';",
        )
        == 1
    ):
        engine.execute(f"DROP TABLESPACE {name};")


@contextlib.contextmanager
def _system_engine(app):
    app_db_url = urllib.parse.urlparse(app.config["SQLALCHEMY_DATABASE_URI"])
    url = urllib.parse.ParseResult(
        scheme=app_db_url.scheme,
        netloc=app_db_url.netloc,
        path="/postgres",
        params=app_db_url.params,
        query=app_db_url.query,
        fragment=app_db_url.fragment,
    ).geturl()
    engine = sa.create_engine(url)
    engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    yield engine
    engine.dispose()


def _get_scalar_result(engine, sql):
    result_proxy = engine.execute(sql)
    result = result_proxy.scalar()
    result_proxy.close()
    return result
