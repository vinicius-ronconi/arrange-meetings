import random
import requests
import ujson
import urllib.parse

from ArrangeMeetings import settings
from places import beans, exceptions
from places.interfaces import IPlacesApi


class GooglePlacesApi(IPlacesApi):
    BASE_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?{}'

    def get_places(self, places_query):
        encoded_query = self._encode_query(places_query)
        response = self._validate_response(requests.get(self.BASE_URL.format(encoded_query)))
        return beans.Places(
            places_list=response.get('results'),
            next_page_token=response.get('next_page_token'),
        )

    def _encode_query(self, query):
        """
        :type query: places.beans.PlacesQuery
        :rtype: str
        """
        make_url_params = self._make_url_params
        if query.next_page_token:
            make_url_params = self._make_next_page_url_params
        return urllib.parse.urlencode(make_url_params(query))

    @staticmethod
    def _make_next_page_url_params(query):
        """
        :type query: places.beans.PlacesQuery
        :rtype: dict
        """
        return {'key': settings.GOOGLE_PLACES_API_KEY, 'pagetoken': query.next_page_token}

    @staticmethod
    def _make_url_params(query):
        """
        :type query: places.beans.PlacesQuery
        :rtype: dict
        """
        query_dict = {
            'key': settings.GOOGLE_PLACES_API_KEY,
            'location': ','.join(map(str, query.location)),
            'radius': query.radius,
            'type': 'restaurant',
        }
        if query.min_price is not None:
            query_dict.update({'minprice': query.min_price})
        if query.max_price:
            query_dict.update({'maxprice': query.max_price})
        if query.open_now:
            query_dict.update({'opennow': True})
        if query.restaurant_type:
            query_dict.update({'keyword': query.restaurant_type})
        return query_dict

    @staticmethod
    def _validate_response(response):
        content = ujson.loads(response.content)
        if content.get('status') not in exceptions.STATUS_TO_EXCEPTION_MAP:
            return content
        exception_class = exceptions.STATUS_TO_EXCEPTION_MAP[content.get('status')]
        raise exception_class(content.get('error_message'))


class FakePlacesApi(IPlacesApi):
    def get_places(self, places_query):
        restaurant_type = 'World Food' if places_query.next_page_token else places_query.restaurant_type
        return beans.Places(
            places_list=[
                {
                    'id': 'restaurant_id_{type}'.format(type=restaurant_type),
                    'name': 'Best {type} restaurant in the World'.format(type=restaurant_type),
                    'opening_hours': {
                        'open_now': bool(random.randint(0,1)),
                    },
                    'rating': float(random.randint(0, 50)) / 10,
                    'types': ['restaurant', 'food'],
                }
            ],
            next_page_token='next_page',
        )