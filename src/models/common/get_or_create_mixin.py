from copy import deepcopy
import arrow

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import insert as pg_insert


class GetOrCreateMixin:
    @classmethod
    def get_or_create(
        cls,
        create_params: dict = None,
        index_elements=None,
        index_where=None,
        **search_by_params
    ):
        """
        Implements 'insert or create' behavior for SQLAlchemy using PostgreSQL UPSERT
        semantics.

        This is both safe and efficient, since it takes only one db roundtrip but it
        comes with caveats and can't work in all cases.

        Internally it is using SQLAlchemy Postgres dialect, details are here:
        https://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#sqlalchemy.dialects.postgresql.dml.Insert.on_conflict_do_update
        https://docs.sqlalchemy.org/en/latest/orm/persistence_techniques.html#using-postgresql-on-conflict-with-returning-to-return-upserted-orm-objects

        Note:

            This **IS** multi-thread and/or multi-process safe but it will work only
            if there is **unique index** on destination table that can be used as
            arbiter when deciding should object be INSERTed or just SELECTed

        Warning:

            Implementation is PostgreSQL speciffic. Minimal PostgreSQL version is 9.6.
            For other RDBMs see `get_or_create_no_index`.

        Arguments:

            create_params: column names and values that will be used for creating new
                row.
            search_by_params: column names and values that will be used to detect what
                arbiter index to use. Thus, keys in this dict must all be column names
                of some unique index. Also, any key and value tuples found in this dict
                will overwrite ones in ``create_params``.
            index_elements: A sequence consisting of string column names, Column
                objects, or other column expression objects that will be used to
                infer a target index. If not provided, ``search_by_params.keys()`` are
                used.
            index_where: Additional WHERE criterion that can be used to infer a
                conditional target index.
        """
        create_params = deepcopy(create_params or {})
        create_params.update(search_by_params)

        # We need to update at least one attribute, otherwise session.execute might
        # return no objects. Since all our objects have "updated_at", this is probably
        # best one to update.
        create_params["updated_at"] = arrow.utcnow().datetime

        statement = (
            pg_insert(cls)
            .values([create_params])
            .on_conflict_do_update(
                index_elements=list(search_by_params.keys())
                if not index_elements
                else index_elements,
                index_where=index_where,
                set_=create_params,
            )
        ).returning(cls)

        orm_stmt = (
            sa.select(cls)
            .from_statement(statement)
            .execution_options(populate_existing=True)
        )

        return cls.query.session.execute(orm_stmt).scalar_one()

    @classmethod
    def get_or_create_only_id(
        cls,
        create_params: dict = None,
        index_elements=None,
        index_where=None,
        **search_by_params
    ):
        """
        Same as ``get_or_create`` but instead of returning whole ORM instance, it only
        returns ID of created / updated row.
        """
        create_params = deepcopy(create_params or {})
        create_params.update(search_by_params)

        # We need to update at least one attribute, otherwise session.execute might
        # return no objects. Since all our objects have "updated_at", this is probably
        # best one to update.
        create_params["updated_at"] = arrow.utcnow().datetime

        statement = (
            pg_insert(cls)
            .values([create_params])
            .on_conflict_do_update(
                index_elements=list(search_by_params.keys())
                if not index_elements
                else index_elements,
                index_where=index_where,
                set_=create_params,
            )
        ).returning(cls.id)

        return cls.query.session.execute(statement).scalar_one()

    @classmethod
    def get_or_create_no_index(cls, create_params: dict = None, **search_by_params):
        """
        Same as `get_or_create` but much slower since it in worst case requires
        multiple roundtrips to db.

        This is to be used when destination table doesn't have any unique index that
        is required by `get_or_create` to operate.

        Warning:
            This is **NOT** multi-thread or multi-proccess safe implementation of
            db UPSERT.
        """
        # TODO: Decouple this whole thing from Flask-SQLAlchemy
        from Hexa.db import db

        retv = None
        try:
            retv = db.session.query(cls).filter_by(**search_by_params).one()

        except orm.exc.NoResultFound:
            create_params = deepcopy(create_params or {})
            create_params.update(search_by_params)
            created = cls(**create_params)

            try:
                db.session.add(created)
                db.session.flush()
                retv = created

            except sa.exc.IntegrityError as e:
                db.session.rollback()
                if "duplicate key value violates unique constraint" in str(e):
                    retv = db.session.query(cls).filter_by(**search_by_params).one()
                    for k, v in create_params.items():
                        setattr(retv, k, v)
                else:
                    raise

        return retv
