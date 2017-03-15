from users import models
from users.dao import beans
from users.dao.interfaces import IUserPreferencesDao


class DbUserPreferencesDao(IUserPreferencesDao):
    def get_user_preferences(self, user_id):
        preferences = models.UserPreferences.objects.get(user_id=user_id)
        return beans.UserPreferences(
            user_id=user_id,
            home_location=preferences.home_location,
            radius_in_meters=preferences.radius_in_meters,
            min_price=preferences.min_price,
            max_price=preferences.max_price,
            restaurant_types=preferences.restaurant_types,
        )
