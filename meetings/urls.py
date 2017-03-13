from django.conf.urls import url
from meetings import views


urlpatterns = [
    url(r'^arrange/', views.ArrangeMeetingView.as_view(), name='arrange_meetings'),
]
