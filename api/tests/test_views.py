from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Transaction


class TransactionViewsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.category = Category.objects.create(name="Test Category")

        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal("100.50"),
            date=timezone.now(),
            category=self.category,
            description="Test transaction description",
            transaction_type="income",
        )

    def test_get_transactions(self):
        url = reverse("get-transactions")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["transactions"]), 1)
        self.assertEqual(
            response.data["transactions"][0]["amount"], str(self.transaction.amount)
        )

    def test_add_transaction(self):
        url = reverse("add-transaction")
        data = {
            "amount": Decimal("150.00"),
            "date": timezone.now(),
            "category": self.category.id,
            "description": "New transaction description",
            "transaction_type": "expense",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Transaction.objects.count(), 2
        )  #  Checking whether new transaction was added

    def test_update_transaction(self):
        url = reverse("update-transaction", args=[self.transaction.id])
        data = {
            "amount": Decimal("200.00"),
            "description": "Updated transaction description",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, Decimal("200.00"))
        self.assertEqual(
            self.transaction.description, "Updated transaction description"
        )

    def test_delete_transaction(self):
        url = reverse("delete-transaction", args=[self.transaction.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            Transaction.objects.count(), 0
        )  # Checking if transaction was deleted

    def test_get_balance(self):
        url = reverse("get-balance")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["income"], self.transaction.amount)
        self.assertEqual(response.data["expenses"], 0)
        self.assertEqual(response.data["balance"], self.transaction.amount)
