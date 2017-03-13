import ujson

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic import View

from meetings.controller import ArrangeMeetingController
from meetings.exceptions import MeetingsException
from places.factory import PlacesApiFactory
from users.factory import UserDaoFactory


class ArrangeMeetingView(View):
    def get(self, request):
        try:
            controller = ArrangeMeetingController(dao=UserDaoFactory.make_dao(), api=PlacesApiFactory.make_api())
            arranged_meeting = controller.arrange_meeting(request)
        except MeetingsException as e:
            return HttpResponseBadRequest(ujson.dumps({'error': str(e)}),content_type='application/json')
        else:
            return HttpResponse(ujson.dumps(self.jsonify_arranged_meeting(arranged_meeting)))

    @staticmethod
    def jsonify_arranged_meeting(arranged_meeting):
        """
        :type arranged_meeting: meetings.beans.ArrangedMeetingOptions
        :rtype: dict
        """
        return {
            'organizer_next_pages': arranged_meeting.organizer_next_pages,
            'invitee_next_pages': arranged_meeting.invitee_next_pages,
            'common_places': arranged_meeting.common_places,
            'invitee_places': arranged_meeting.invitee_places,
        }
