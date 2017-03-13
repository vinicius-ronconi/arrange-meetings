from collections import namedtuple


class ArrangedMeetingOptions(namedtuple('ArrangedMeetingOptions', [
    'organizer_next_pages',  # dict
    'invitee_next_pages',  # dict
    'common_places',  # list(dict)
    'invitee_places',  # list(dict)
])):
    pass


class PlacesOptions(namedtuple('PlacesOptions', [
    'places',  # list(dict)
    'next_pages',  # dict
])):
    pass
