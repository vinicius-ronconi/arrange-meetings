from ArrangeMeetings import settings
from places.api import GooglePlacesApi, FakePlacesApi


class PlacesApiFactory(object):
    @classmethod
    def make_api(cls):
        """
        :rtype: places.interfaces.IPlacesApi
        """
        if settings.USE_FAKE_DATA:
            return cls._make_fake_api()
        else:
            return cls._make_google_api()

    @staticmethod
    def _make_fake_api():
        return FakePlacesApi()

    @staticmethod
    def _make_google_api():
        return GooglePlacesApi()
