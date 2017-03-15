from django.test import TestCase

from ArrangeMeetings import settings
from users.dao import beans
from users.factory import UserDaoFactory
from users.models import UserPreferences


class DbDaoTestCase(TestCase):
    USER_ID = 1
    settings.USE_FAKE_DATA = False
    dao = UserDaoFactory.make_dao()

    def setUp(self):
        UserPreferences.objects.all().delete()
        UserPreferences(
            user_id=self.USER_ID,
            home_location=(-20.2877528, -40.2932812),
            min_price=0,
            max_price=4,
            radius_in_meters=5000,
            restaurant_types=['italian', 'brazilian', 'BBQ']
        ).save()

    def tearDown(self):
        UserPreferences.objects.all().delete()

    def test_it_raises_does_not_exist_exception(self):
        self.assertRaises(UserPreferences.DoesNotExist, self.dao.get_user_preferences, user_id=2)

    def test_it_returns_bean(self):
        preferences = self.dao.get_user_preferences(self.USER_ID)
        self.assertIsInstance(preferences, beans.UserPreferences)
        self.assertEqual(preferences.user_id, self.USER_ID)


class FakeDaoTestCase(TestCase):
    settings.USE_FAKE_DATA = True
    dao = UserDaoFactory.make_dao()

    def test_it_returns_bean(self):
        self.assertEqual(UserPreferences.objects.all().count(), 0)
        preferences = self.dao.get_user_preferences(user_id=1)
        self._assert_fake_user(preferences, user_id=1, radius=5000)

        preferences = self.dao.get_user_preferences(user_id=2)
        self._assert_fake_user(preferences, user_id=2, radius=1000)

        preferences = self.dao.get_user_preferences(user_id=3)
        self._assert_fake_user(preferences, user_id=3, radius=20000)

    def _assert_fake_user(self, preferences, user_id, radius):
        self.assertIsInstance(preferences, beans.UserPreferences)
        self.assertEqual(preferences.user_id, user_id)
        self.assertEqual(preferences.radius_in_meters, radius)
