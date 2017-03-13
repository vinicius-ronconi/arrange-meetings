from collections import namedtuple


class UserPreferences(namedtuple('UserPreferences', [
    'user_id',  # int
    'home_location',  # tuple
    'radius_in_meters',  # tuple
    'min_price',  # int
    'max_price',  # int
    'restaurant_types',  # list(str)
])):
    pass
