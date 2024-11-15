from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from user.models import Profile


class ProfileModelTest(TestCase):

    def test_profile_creation(self):
        # Tworzymy użytkownika
        user = User.objects.create_user(username="testuser", password="testpassword")

        # Sprawdzamy, czy profil został automatycznie utworzony dla nowego użytkownika
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, user)

    def test_profile_reset_password_token(self):
        user = User.objects.create_user(username="testuser2", password="testpassword")
        profile = Profile.objects.get(user=user)
        profile.reset_password_token = "testtoken"
        profile.reset_password_expire = timezone.now()
        profile.save()

        # Sprawdzamy, czy wartości zostały poprawnie zapisane
        self.assertEqual(profile.reset_password_token, "testtoken")
        self.assertIsNotNone(profile.reset_password_expire)
