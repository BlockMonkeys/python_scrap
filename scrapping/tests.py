from django.test import TestCase
from django.urls import resolve
from scrapping.views import index
from django.http import HttpRequest

# Create your tests here.
class AppTest(TestCase):

    # def test_resolve_to_index(self):
    #     found = resolve("/")
    #     print(found)
    #     self.assertEqual(found.func, index)

    def test_index_page_returns_correct_html(self):
        request = HttpRequest()
        resp = index(request)
        self.assertTrue(resp.content.startswith(b'<html>'))
        self.assertIn(b'<title>To-Do Lists</title>', resp.content)
        self.assertTrue(resp.content.endswith(b'</html>'))