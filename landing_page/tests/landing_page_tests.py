from django.test import TestCase


class LandingPageTestCase(TestCase):
    def test_it_returns_http_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
