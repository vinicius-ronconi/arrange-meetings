import mock
import ujson
from django.core.urlresolvers import reverse
from django.test import TestCase

from places.interfaces import IPlacesApi
from places.api import FakePlacesApi
from places.exceptions import NoDataFoundException
from users.dao.interfaces import IUserPreferencesDao


class FakePreferencesDao(IUserPreferencesDao):
    def get_user_preferences(self, user_id):
        from users.dao.beans import UserPreferences
        if user_id == 1:
            return UserPreferences(
                user_id=user_id,
                home_location=(-20.2882, -40.2935),
                radius_in_meters=8000,
                min_price=1,
                max_price=3,
                restaurant_types=['japanese', 'italian', 'BBQ', 'mexican', 'vegan', 'hamburger'],
            )
        elif user_id == 2:
            return UserPreferences(
                user_id=user_id,
                home_location=(-20.2850, -40.3000),
                radius_in_meters=10000,
                min_price=0,
                max_price=4,
                restaurant_types=['italian', 'BBQ', 'mexican', 'hamburger'],
            )
        elif user_id == 3:
            return UserPreferences(
                user_id=user_id,
                home_location=(-20.2900, -40.3000),
                radius_in_meters=10000,
                min_price=0,
                max_price=4,
                restaurant_types=['canadian'],
            )
        elif user_id == 4:
            return UserPreferences(
                user_id=user_id,
                home_location=(-20.2900, -40.3000),
                radius_in_meters=10000,
                min_price=4,
                max_price=4,
                restaurant_types=['japanese', 'italian', 'BBQ', 'mexican', 'vegan', 'hamburger'],
            )
        elif user_id == 5:
            return UserPreferences(
                user_id=user_id,
                home_location=(-11.0000, -11.0000),
                radius_in_meters=100,
                min_price=4,
                max_price=4,
                restaurant_types=['japanese', 'italian', 'BBQ', 'mexican', 'vegan', 'hamburger'],
            )


class NoPlaceFakeApi(IPlacesApi):
    def get_places(self, places_query):
        from places.beans import Places
        return Places(places_list=[], next_page_token='')


class NoDataFoundFakeApi(IPlacesApi):
    def get_places(self, places_query):
        raise NoDataFoundException()


class ArrangedMeetingTestCase(TestCase):
    def setUp(self):
        self._mock_user_preferences_dao()
        self._mock_places_api()

    def _mock_user_preferences_dao(self):
        preferences_patcher = mock.patch('users.factory.UserDaoFactory.make_dao', return_value=FakePreferencesDao())
        preferences_patcher.start()
        self.addCleanup(preferences_patcher.stop)

    def _mock_places_api(self):
        places_patcher = mock.patch('places.factory.PlacesApiFactory.make_api', return_value=FakePlacesApi())
        self.mocked_places_api = places_patcher.start()
        self.addCleanup(places_patcher.stop)

    def test_it_invitee_has_no_place(self):
        self.mocked_places_api.return_value = NoPlaceFakeApi()
        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 5})
        content = self._assert_it_returns_arranged_meetings(response)
        self._assert_no_matches(content, has_place=False)

    def test_it_invitee_raises_no_data_found_exception(self):
        self.mocked_places_api.return_value = NoDataFoundFakeApi()
        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 5})
        content = self._assert_it_returns_arranged_meetings(response)
        self._assert_no_matches(content, has_place=False)

    def test_it_returns_only_invitees_places_when_no_restaurant_type_matches(self):
        self.mocked_places_api.return_value = FakePlacesApi()
        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 3})
        content = self._assert_it_returns_arranged_meetings(response)
        self._assert_no_matches(content, has_place=True)

    def test_it_returns_only_invitees_places_when_no_price_range_matches(self):
        self.mocked_places_api.return_value = FakePlacesApi()
        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 4})
        content = self._assert_it_returns_arranged_meetings(response)
        self._assert_no_matches(content, has_place=True)

    def test_it_uses_pages_token_when_it_is_present_on_the_request(self):
        # TODO
        pass

    def test_it_returns_common_places(self):
        self.mocked_places_api.return_value = FakePlacesApi()
        response = self.client.get(
            reverse('arrange_meetings'),
            data={'organizer_id': 1, 'invitee_id': 2, 'restaurant_types': 'japanese , bbq , italian , mexican'}
        )
        content = self._assert_it_returns_arranged_meetings(response)
        self._assert_matches(content)

    def _assert_it_returns_arranged_meetings(self, response):
        self.assertEqual(response.status_code, 200)
        content = ujson.loads(response.content)
        self.assertIsInstance(content, dict)
        self.assertIn('organizer_next_pages', content)
        self.assertIn('invitee_next_pages', content)
        self.assertIn('common_places', content)
        self.assertIn('invitee_places', content)
        return content

    def _assert_no_matches(self, content, has_place):
        self.assertEqual(content.get('organizer_next_pages'), None)
        self.assertEqual(content.get('common_places'), None)
        self.assertIsInstance(content.get('invitee_next_pages'), dict)
        self.assertIsInstance(content.get('invitee_places'), list)
        self.assertEqual(len(content.get('invitee_places')) > 0, has_place)

    def _assert_matches(self, content):
        self.assertIsInstance(content.get('organizer_next_pages'), dict)
        self.assertIsInstance(content.get('common_places'), list)
        self.assertTrue(len(content.get('common_places')) > 0)
        self.assertIsInstance(content.get('invitee_next_pages'), dict)
        self.assertIsInstance(content.get('invitee_places'), list)

    def test_it_raises_exception_for_missing_parameters(self):
        response = self.client.get(reverse('arrange_meetings'), data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('organizer_id', ujson.loads(response.content).get('error'))

        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn('invitee_id', ujson.loads(response.content).get('error'))

    def test_it_raises_exception_for_invalid_parameter_values(self):
        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 'a', 'invitee_id': 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn('organizer_id', ujson.loads(response.content).get('error'))

        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 'a'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('invitee_id', ujson.loads(response.content).get('error'))

        response = self.client.get(reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn('invitee_id', ujson.loads(response.content).get('error'))

        self._assert_param_in_range('min_price', invalid_value=5)
        self._assert_param_in_range('max_price', invalid_value=5)
        self._assert_param_in_range('radius', invalid_value=500000)
        self._assert_param_in_range('organizer_location', invalid_value='200,200')
        self._assert_param_in_range('organizer_location', invalid_value='20,200')

    def _assert_param_in_range(self, param_name, invalid_value):
        response = self.client.get(
            reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 2, param_name: invalid_value}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(param_name, ujson.loads(response.content).get('error'))

        response = self.client.get(
            reverse('arrange_meetings'), data={'organizer_id': 1, 'invitee_id': 2, param_name: 'a'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(param_name, ujson.loads(response.content).get('error'))
