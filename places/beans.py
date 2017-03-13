from collections import namedtuple


class Places(namedtuple('Places', [
    'places_list',  # list(dict)
    'next_page_token',  # str
])):
    pass


class PlacesQuery(namedtuple('PlacesQuery', [
    'next_page_token',  # str
    'location',  # tuple
    'radius',  # int
    'min_price',  # int
    'max_price',  # int
    'open_now',  # bool
    'restaurant_type',  # str
])):
    pass