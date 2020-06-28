from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='test@ekocibar.com',
            password='test1234'
        )
        # Use built in method to login
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@ekocibar2.com',
            password='test1234',
            name='Test user name'
        )

    def test_users_listed(self):
        """Test that users are listed on the page"""
        # Use built in reverse, params first app then url end point
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        # Check whether response is 200 and contains data
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the user add page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
