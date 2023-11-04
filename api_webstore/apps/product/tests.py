from django.test import TestCase

from apps.product


class DataTestCase(TestCase):
    def test_minus(self):
        result = operations(2, 3, '-')
        self.assertEqual(6, result)