import sqlalchemy as sa
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


def table_name_shortener(constraint, table):
    tokens = table.name.split("_")
    if len(tokens) > 2 or len(table.name) > 30:
        return "_".join([_[:3] for _ in tokens[:-1]] + tokens[-1:])
    return table.name


def index_prefix_generator(constraint, table):
    return "ix_uq" if getattr(constraint, "unique", None) else "ix"


def check_constraint_prefix_generator(constraint, table):
    columns = list(constraint.columns)
    if len(columns) == 1 and isinstance(columns[0].type, sa.Enum):
        return "ck_enm"
    return "ck"


db = SQLAlchemy(
    metadata=MetaData(
        naming_convention={
            "short_table_name": table_name_shortener,
            "index_prefix": index_prefix_generator,
            "check_prefix": check_constraint_prefix_generator,
            "ix": "%(index_prefix)s_%(short_table_name)s_%(column_0_name)s",
            "uq": "uq_%(short_table_name)s_%(column_0_name)s",
            "ck": "%(check_prefix)s_%(short_table_name)s_%(column_0_name)s",
            "fk": "fk_%(short_table_name)s_%(column_0_name)s",
            "pk": "pk_%(short_table_name)s",
        }
    ),
)

migrate = Migrate()
