from django.test import TestCase
from api.models import Category
from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Transaction, Category
from decimal import Decimal
from django.utils import timezone

class CategoryModelTest(TestCase):

    def setUp(self):
        # Set category instance used in tests
        self.category = Category.objects.create(name="Test Category")

    def test_category_creation(self):
        # Test if instance used in test was correctly set
        self.assertEqual(self.category.name, "Test Category")
        self.assertIsInstance(self.category, Category)

    def test_str_method(self):
        #  Test if method __str__ return correct value
        self.assertEqual(str(self.category), "Test Category")

    def test_category_name_max_length(self):
        max_length = self.category._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)


class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')


        self.category = Category.objects.create(name="Test Category")

        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.50'),
            date=timezone.now(),
            category=self.category,
            description="Test transaction description",
            transaction_type='income'
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.amount, Decimal('100.50'))
        self.assertEqual(self.transaction.transaction_type, 'income')
        self.assertEqual(self.transaction.category.name, "Test Category")
        self.assertEqual(self.transaction.user.username, 'testuser')


    def test_str_method(self):
        expected_str = f'{self.transaction.user} - {self.transaction.amount} ({self.transaction.transaction_type})'
        self.assertEqual(str(self.transaction), expected_str)

    def test_transaction_type_choices(self):
        # Test if transaction_field has corret values to choose
        transaction_type_field = self.transaction._meta.get_field('transaction_type')
        self.assertEqual(transaction_type_field.choices, [('income', 'Income'), ('expense', 'Expense')])

    def test_amount_precision(self):
        self.assertEqual(self.transaction.amount, Decimal('100.50'))
        self.assertLessEqual(self.transaction.amount.as_tuple().exponent, -2) # Precision check up to 2 decimal places

    def test_foreign_key_relationships(self):
        self.assertEqual(self.transaction.category, self.category)
        self.assertEqual(self.transaction.user, self.user)



