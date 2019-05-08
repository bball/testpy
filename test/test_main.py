from unittest import TestCase, skip
from main.main import get_val


class TestMain(TestCase):
    def test_gen_val(self):
        self.assertEqual(get_val(), 1)

    #@skip('SKIP')
    def test_gen_val_fail(self):
        self.assertEqual(get_val(), 2)
