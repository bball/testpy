from unittest import TestCase
from main.main import get_val


class TestMain(TestCase):
    def test_gen_val(self):
        self.assertEqual(get_val(), 1)

    def test_gen_val_fail(self):
        self.assertEqual(get_val(), 2)
