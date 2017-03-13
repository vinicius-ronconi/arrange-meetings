from ArrangeMeetings import settings
from users.dao.db_dao import DbUserPreferencesDao
from users.dao.fake_dao import FakeUserPreferencesDao


class UserDaoFactory(object):
    @classmethod
    def make_dao(cls):
        if settings.USE_FAKE_DATA:
            return cls._make_fake_dao()
        else:
            return cls._make_db_dao()

    @staticmethod
    def _make_fake_dao():
        return FakeUserPreferencesDao()

    @staticmethod
    def _make_db_dao():
        return DbUserPreferencesDao()
