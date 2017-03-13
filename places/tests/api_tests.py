import mock
from django.test import TestCase

from ArrangeMeetings import settings
from places import beans, exceptions
from places.factory import PlacesApiFactory


class MockedResponse(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


class PlacesApiTestCase(TestCase):
    api = NotImplemented

    @staticmethod
    def _make_next_page_query(next_page_token):
        return beans.PlacesQuery(
            next_page_token=next_page_token,
            location=None,
            radius=None,
            min_price=None,
            max_price=None,
            open_now=None,
            restaurant_type=None,
        )

    @staticmethod
    def _make_initial_query(min_price=None, max_price=None, open_now=None, restaurant_type=None):
        return beans.PlacesQuery(
            next_page_token=None,
            location=(-19, -19),
            radius=1000,
            min_price=min_price,
            max_price=max_price,
            open_now=open_now,
            restaurant_type=restaurant_type,
        )


class GooglePlacesApiTestCase(PlacesApiTestCase):
    settings.USE_FAKE_DATA = False
    api = PlacesApiFactory.make_api()

    @mock.patch('places.api.requests')
    def test_it_requests_first_page(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"results" : [{"p1": 1}, {"p2": 2}],\n"status" : "OK"\n}'
        )
        query = self._make_initial_query()
        places = self.api.get_places(query)
        self.assertIsInstance(places, beans.Places)
        self.assertIsInstance(places.places_list, list)
        self.assertEqual(m_requests.get.call_count, 1)

        requested_url = m_requests.get.call_args[0][0]
        self.assertIn('location', requested_url)
        self.assertIn('radius', requested_url)
        self.assertNotIn('pagetoken', requested_url)

        self.assertNotIn('minprice', requested_url)
        self.assertNotIn('maxprice', requested_url)
        self.assertNotIn('opennow', requested_url)
        self.assertNotIn('keyword', requested_url)

        query = self._make_initial_query(min_price=0, max_price=4, open_now=True, restaurant_type='bbq')
        places = self.api.get_places(query)
        self.assertIsInstance(places, beans.Places)
        self.assertIsInstance(places.places_list, list)
        self.assertEqual(m_requests.get.call_count, 2)

        requested_url = m_requests.get.call_args[0][0]
        self.assertIn('location', requested_url)
        self.assertIn('radius', requested_url)
        self.assertNotIn('pagetoken', requested_url)

        self.assertIn('minprice=0', requested_url)
        self.assertIn('maxprice=4', requested_url)
        self.assertIn('opennow', requested_url)
        self.assertIn('keyword=bbq', requested_url)

    @mock.patch('places.api.requests')
    def test_it_requests_next_page(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"results" : [{"p1": 1}, {"p2": 2}],\n"status" : "OK"\n}'
        )
        query = self._make_next_page_query('some_token')
        places = self.api.get_places(query)
        self.assertIsInstance(places, beans.Places)
        self.assertIsInstance(places.places_list, list)
        self.assertEqual(m_requests.get.call_count, 1)

        requested_url = m_requests.get.call_args[0][0]
        self.assertIn('pagetoken', requested_url)
        self.assertNotIn('location', requested_url)
        self.assertNotIn('radius', requested_url)

    @mock.patch('places.api.requests')
    def test_it_raises_no_data_found_exception(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"error_message" : "some_error",\n"results" : [],\n"status" : "ZERO_RESULTS"\n}'
        )
        query = self._make_next_page_query('some_token')
        self.assertRaises(exceptions.NoDataFoundException, self.api.get_places, query)

    @mock.patch('places.api.requests')
    def test_it_raises_request_denied_exception(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"error_message" : "some_error",\n"results" : [],\n"status" : "REQUEST_DENIED"\n}'
        )
        query = self._make_next_page_query('some_token')
        self.assertRaises(exceptions.RequestDeniedException, self.api.get_places, query)

    @mock.patch('places.api.requests')
    def test_it_raises_exceeded_quota_exception(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"error_message" : "some_error",\n"results" : [],\n"status" : "OVER_QUERY_LIMIT"\n}'
        )
        query = self._make_next_page_query('some_token')
        self.assertRaises(exceptions.ExceededQuotaException, self.api.get_places, query)

    @mock.patch('places.api.requests')
    def test_it_raises_invalid_request_exception(self, m_requests):
        m_requests.get.return_value = MockedResponse(
            status_code=200,
            content=b'{\n"error_message" : "some_error",\n"results" : [],\n"status" : "INVALID_REQUEST"\n}'
        )
        query = self._make_next_page_query('some_token')
        self.assertRaises(exceptions.InvalidRequestException, self.api.get_places, query)


class FakePlacesApiTestCase(PlacesApiTestCase):
    settings.USE_FAKE_DATA = True
    api = PlacesApiFactory.make_api()

    def test_it_requests_first_page(self):
        self._test_it_requests_fake_data(self._make_initial_query())

    def test_it_requests_next_page(self):
        self._test_it_requests_fake_data(self._make_next_page_query('next_page_token'))

    def _test_it_requests_fake_data(self, query):
        places = self.api.get_places(query)
        self.assertIsInstance(places, beans.Places)
        self.assertIsInstance(places.places_list, list)
        self.assertIn('id', places.places_list[0])
