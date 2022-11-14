from src import ListItem
from src.general import Status


class ListItemService:

    def __init__(self, listitem=ListItem()):
        self.listitem = listitem

    def create(self):
        self.listitem.add()
        self.listitem.commit_or_rollback()

        return Status.successfully_processed()

    @classmethod
    def get_one(cls, _id):
        return cls(listitem=ListItem.query.get_one(_id=_id))

    @staticmethod
    def get_all_increasing_categories():
        data = ListItem.query.get_all_increasing_categories()

        return data

    @staticmethod
    def get_category_prefix(_id):
        data = ListItem.query.get_category_prefix(_id=_id)
        return data
