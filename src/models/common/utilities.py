import sys

import sqlalchemy as sa

try:
    import pygments
    from pygments.formatters import Terminal256Formatter

    # from pygments.formatters import TerminalTrueColorFormatter
    from pygments.lexers import SqlLexer

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


try:
    import sqlparse

    HAS_SQLPARSE = True
except ImportError:
    HAS_SQLPARSE = False


def print_sql(sql, file=sys.stdout, flush=False):
    sql = str(sql)

    if HAS_SQLPARSE:
        sql = sqlparse.format(sql, reindent=True, keyword_case="upper").strip()

    if HAS_PYGMENTS and file == sys.stdout:
        sql = pygments.highlight(
            sql, SqlLexer(), Terminal256Formatter(style="monokai")
        ).strip()

    print(sql, file=file, flush=flush)


def log_sql(title, sql, logger, engine=None):
    if engine and hasattr(sql, "compile"):
        sql = str(sql.compile(engine, compile_kwargs={"literal_binds": True}))
    else:
        sql = str(sql)

    if HAS_SQLPARSE:
        sql = sqlparse.format(sql, reindent=True, keyword_case="upper").strip()

    if HAS_PYGMENTS:
        sql = pygments.highlight(
            sql, SqlLexer(), Terminal256Formatter(style="monokai")
        ).strip()

    logger.debug(
        title + " %s" if title else "%s",
        " ".join((_.strip() for _ in sql.splitlines())),
    )


def all_models():
    # TODO We shuld probably use importlib to implement more generic solution for this
    # without explicitly using app name to import module
    import flask_sqlalchemy

    from Hexa import models

    for klass in models.__dict__.values():
        if isinstance(klass, type) and issubclass(klass, flask_sqlalchemy.model.Model):
            yield klass
