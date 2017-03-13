from abc import ABCMeta, abstractmethod


class IPlacesApi(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_places(self, places_query):
        """
        :type places_query: places.beans.PlacesQuery
        :rtype: list(dict)
        """
