from operator import itemgetter
from meetings import beans, exceptions
from users.dao.beans import UserPreferences
from places.beans import PlacesQuery


class ArrangeMeetingController(object):
    REQUIRED_PARAMETERS = ['organizer_id', 'invitee_id']

    def __init__(self, dao, api):
        self.dao = dao
        self.api = api

    def arrange_meeting(self, request):
        request = self._validate_request(request)

        open_now = bool(request.GET.get('open_now'))
        organizer_next_pages = request.GET.get('organizer_next_pages')
        invitee_next_pages = request.GET.get('invitee_next_pages')

        organizer_id = int(request.GET.get('organizer_id'))
        invitee_id = int(request.GET.get('invitee_id'))
        organizer_preferences = self._get_organizer_preferences(organizer_id, request)
        invitee_preferences = self.dao.get_user_preferences(invitee_id)

        common_types = self._get_common_restaurant_types(organizer_preferences, invitee_preferences)
        min_common_price, max_common_price = self._get_common_price_range(organizer_preferences, invitee_preferences)

        invitee_places = self._get_places(
            invitee_preferences,
            invitee_next_pages or {},
            common_types or invitee_preferences.restaurant_types,
            min_common_price or invitee_preferences.min_price,
            max_common_price or invitee_preferences.max_price,
            open_now,
        )

        if not common_types or min_common_price is None:
            return beans.ArrangedMeetingOptions(
                organizer_next_pages=None,
                invitee_next_pages=invitee_places.next_pages,
                common_places=None,
                invitee_places=invitee_places.places,
            )

        organizer_places = self._get_places(
            organizer_preferences,
            organizer_next_pages or {},
            common_types or organizer_preferences.restaurant_types,
            min_common_price or organizer_preferences.min_price,
            max_common_price or organizer_preferences.max_price,
            open_now,
        )

        invitee_places_ids = list(map(itemgetter('id'), invitee_places.places))
        organizer_places_ids = list(map(itemgetter('id'), organizer_places.places))
        common_places_ids = list(set(invitee_places_ids) & set(organizer_places_ids))

        return beans.ArrangedMeetingOptions(
            organizer_next_pages=organizer_places.next_pages,
            invitee_next_pages=invitee_places.next_pages,
            common_places=[place for place in invitee_places.places if place.get('id') in common_places_ids],
            invitee_places=[place for place in invitee_places.places if place.get('id') not in common_places_ids],
        )

    def _get_organizer_preferences(self, organizer_id, request):
        preset_preferences = self.dao.get_user_preferences(organizer_id)
        restaurant_types = preset_preferences.restaurant_types
        request_restaurant_types = request.GET.get('restaurant_types')
        if request_restaurant_types:
            restaurant_types = [restaurant.strip() for restaurant in request_restaurant_types.split(',')]
        return UserPreferences(
            user_id=organizer_id,
            home_location=self._get_location_from_request(request)[0] or preset_preferences.home_location,
            radius_in_meters=request.GET.get('radius') or preset_preferences.radius_in_meters,
            min_price=request.GET.get('min_price') or preset_preferences.min_price,
            max_price=request.GET.get('max_price') or preset_preferences.max_price,
            restaurant_types=restaurant_types,
        )

    def _validate_request(self, request):
        self._validate_required_parameters(request)

        self._validate_int_range(request, param_name='min_price', min_value=0, max_value=4)
        self._validate_int_range(request, param_name='max_price', min_value=0, max_value=4)
        self._validate_int_range(request, param_name='radius', min_value=0, max_value=20000)

        self._validate_organizer_location(request)
        self._validate_invitee_is_not_organizer(request)

        return request

    def _validate_required_parameters(self, request):
        for param_name in self.REQUIRED_PARAMETERS:
            if param_name not in request.GET:
                raise exceptions.RequiredParameterException('Parameter {} was not found'.format(param_name))
            try:
                int(request.GET.get(param_name))
            except ValueError:
                raise exceptions.InvalidParameterException('Parameter {} should be a number'.format(param_name))

    @staticmethod
    def _validate_int_range(request, param_name, min_value, max_value):
        try:
            param_value = int(request.GET.get(param_name, min_value))
        except ValueError:
            raise exceptions.InvalidParameterException('Parameter {} should be a number'.format(param_name))

        if not (min_value <= param_value <= max_value):
            raise exceptions.InvalidParameterException('Parameter {} should be between {} and {}'.format(
                param_name, min_value, max_value
            ))

    def _validate_organizer_location(self, request):
        if 'organizer_location' not in request.GET:
            return
        try:
            latitude, longitude = self._get_location_from_request(request)
        except ValueError:
            raise exceptions.InvalidParameterException('Parameter organizer_location should be a tuple for float')
        if not (-90 <= latitude <= 90):
            raise exceptions.InvalidParameterException('organizer_location latitude should be between -90 and 90')
        if not (-180 <= longitude <= 180):
            raise exceptions.InvalidParameterException('organizer_location longitude should be between -180 and 180')

    @staticmethod
    def _validate_invitee_is_not_organizer(request):
        if request.GET.get('organizer_id') == request.GET.get('invitee_id'):
            raise exceptions.InvalidParameterException('invitee_id cannot be equal to organizer_id')

    @staticmethod
    def _get_location_from_request(request):
        location = request.GET.get('organizer_location')
        return list(map(float, location.split(','))) if location else [None, None]

    @staticmethod
    def _get_common_restaurant_types(organizer_preferences, invitee_preferences):
        """
        :type organizer_preferences: users.dao.beans.UserPreferences
        :type invitee_preferences: users.dao.beans.UserPreferences
        :type: list(str)
        """
        return list(set(organizer_preferences.restaurant_types) & set(invitee_preferences.restaurant_types))

    @staticmethod
    def _get_common_price_range(organizer_preferences, invitee_preferences):
        """
        :type organizer_preferences: users.dao.beans.UserPreferences
        :type invitee_preferences: users.dao.beans.UserPreferences
        :rtype: tuple
        """
        highest_min_price = max(organizer_preferences.min_price, invitee_preferences.min_price)
        lowest_max_price = min(organizer_preferences.max_price, invitee_preferences.max_price)
        return (highest_min_price, lowest_max_price) if highest_min_price <= lowest_max_price else (None, None)

    def _get_places(self, user_preferences, next_pages, restaurant_types, min_price, max_price, open_now):
        """
        :type user_preferences: users.dao.bean.UserPreferences
        :type next_pages: dict
        :type restaurant_types: list(str)
        :type min_price: int
        :type max_price: int
        :type open_now: bool
        :rtype: meetings.beans.PlacesOptions
        """
        all_places = []
        next_pages_tokens = {}
        for restaurant_type in restaurant_types:
            places = self.api.get_places(PlacesQuery(
                next_page_token=next_pages.get(restaurant_type),
                location=user_preferences.home_location,
                radius=user_preferences.radius_in_meters,
                min_price=min_price,
                max_price=max_price,
                open_now=open_now,
                restaurant_type=restaurant_type,
            ))
            all_places += places.places_list
            next_pages_tokens[restaurant_type] = places.next_page_token
        return beans.PlacesOptions(
            places=all_places,
            next_pages=next_pages_tokens,
        )
