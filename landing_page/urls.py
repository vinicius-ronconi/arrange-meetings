from django.conf.urls import url
from landing_page import views


urlpatterns = [
    url(r'', views.LandingPageView.as_view(), name='landing_page'),
]
