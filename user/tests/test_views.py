from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from user.models import Profile


class UserTests(APITestCase):

    def setUp(self):
        # Creating user to test
        self.user = User.objects.create_user(
            username='john@example.com',
            email='john@example.com',
            password='password123'
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)

        # Setting token and date of expire
        self.profile.reset_password_token = 'testtoken'
        self.profile.reset_password_expire = timezone.now() + timedelta(minutes=10)
        self.profile.save()

    def test_register_user(self):
        url = reverse('register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john2@example.com',  # other email
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # check if other user has been added
        self.assertEqual(User.objects.get(email='john2@example.com').email, 'john2@example.com')

    def test_register_existing_user(self):
        url = reverse('register')
        data = {
            'first_name': 'Cristiano',
            'last_name': 'Ronaldo',
            'email': 'john@example.com',  # Reusing the same email
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_user(self):
        self.client.force_authenticate(user=self.user)  # Login user
        url = reverse('current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'john@example.com')  # Corrected the expected email

    def test_update_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update_user')
        data = {
            'first_name': 'Leo',
            'last_name': 'Messi',
            'email': 'leo@example.com',
            'password': ''
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Refreshing database
        self.assertEqual(self.user.first_name, 'Leo')
        self.assertEqual(self.user.email, 'leo@example.com')

    def test_reset_password_success(self):
        url = reverse('reset_password', args=['testtoken'])  # Changed to correct token
        data = {
            'password': 'newpassword123',
            'confirmPassword': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['details'], 'Password reset successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_reset_password_token_expired(self):
        # Setting expired token
        self.profile.reset_password_expire = timezone.now() - timedelta(minutes=1)
        self.profile.save()

        url = reverse('reset_password', args=['testtoken'])  # Use the correct token
        data = {
            'password': 'newpassword123',
            'confirmPassword': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token is expired')

    def test_reset_password_mismatched_passwords(self):
        url = reverse('reset_password', args=['testtoken'])  # Use the correct token
        data = {
            'password': 'newpassword123',
            'confirmPassword': 'newpassword456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Passwords are not the same')

    def test_reset_password_missing_fields(self):
        url = reverse('reset_password', args=['testtoken'])  # Use the correct token
        data = {
            'password': 'newpassword123',
            # Lack confirmPassword
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Both password fields are required')



