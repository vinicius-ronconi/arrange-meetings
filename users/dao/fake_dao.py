import random
from users.dao.beans import UserPreferences
from users.dao.interfaces import IUserPreferencesDao


class FakeUserPreferencesDao(IUserPreferencesDao):
    LATITUDE = -20.0
    LONGITUDE = -19.0

    RESTAURANT_TYPES = [
        'italian',
        'brazilian',
        'japanese',
        'BBQ',
        'mexican',
        'vegan',
    ]

    def get_user_preferences(self, user_id):
        radius_in_meters = 5000
        min_price = 0
        max_price = 4
        latitude = self.LATITUDE - float(random.randint(0, 9999999)) / 10000000
        longitude = self.LONGITUDE - float(random.randint(0, 9999999)) / 10000000

        if user_id % 3 == 0:
            radius_in_meters = 20000
            restaurant_types = [
                self.RESTAURANT_TYPES[1], self.RESTAURANT_TYPES[2], self.RESTAURANT_TYPES[3], self.RESTAURANT_TYPES[4],
            ]
        elif user_id % 3 == 1:
            max_price = 2
            restaurant_types = [
                self.RESTAURANT_TYPES[0], self.RESTAURANT_TYPES[1], self.RESTAURANT_TYPES[2],
            ]
        else:
            min_price = 3
            radius_in_meters = 1000
            restaurant_types = [
                self.RESTAURANT_TYPES[3], self.RESTAURANT_TYPES[4], self.RESTAURANT_TYPES[5],
            ]
        return UserPreferences(
            user_id=user_id,
            home_location=(latitude, longitude),
            radius_in_meters=radius_in_meters,
            min_price=min_price,
            max_price=max_price,
            restaurant_types=restaurant_types,
        )
