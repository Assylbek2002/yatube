from django.test import TestCase
from .utils import convert_morse


class TestStringMethods(TestCase):
    def test_convert(self):
        result = convert_morse("Привет", "ru")
        self.assertEqual(result, ".--..-....--.-")

    def test_input(self):
        with self.assertRaises(ValueError):
            convert_morse("Привет", "en")

