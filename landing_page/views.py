from django.shortcuts import render
from django.views.generic import View


class LandingPageView(View):
    def get(self, request):
        return render(request, 'landing_page/main.html')
