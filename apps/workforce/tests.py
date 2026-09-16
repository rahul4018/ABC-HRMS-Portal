from django.test import TestCase


class WorkforceSmokeTest(TestCase):
    def test_app_loads(self):
        from .models import ExitCase, FinalSettlement
        self.assertTrue(ExitCase)
        self.assertTrue(FinalSettlement)
