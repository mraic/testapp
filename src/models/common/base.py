import textwrap
from typing import Dict, List, Union

import sqlalchemy as sa

from .sqlalchemy_repr import PrettyRepresentableBase
from .timestamped_model_mixin import TimestampedModelMixin

ErrorsDict = Dict[str, Union[str, List[str]]]


def T(text):
    return textwrap.dedent(" ".join(_.strip() for _ in text.split("\n")))


class BaseQueryMixin:
    pass


class BaseModelMixin(TimestampedModelMixin, PrettyRepresentableBase):
    def __init__(self, *args, **kwargs):
        self._validation_errors = dict()
        super().__init__(*args, **kwargs)

    def related_obj(self, named, fk_name=None):
        """
        Enforces related object resolution in cases where numeric IDs are used to
        create SQLAlchemy relations.

        Note:
            Instead of relying on this method, use correct way of relating SQLAlchemy
            objects!
        """

        # u = User.query.last()
        # b = Book(author_id=u.id)
        # b.author is None
        # => True
        # a = b.related_obj("author")
        # b.author is None
        # => True
        # a is None
        # => False
        if getattr(self, fk_name or f"{named}_id") and not getattr(self, named):
            self_class = sa.inspect(self).class_
            remote_class = sa.inspect(getattr(self_class, named)).entity.class_
            return remote_class.query.get(getattr(self, fk_name or f"{named}_id"))

        return getattr(self, named)
