## This RESTful application is a financial transaction management system built using Django and Django REST Framework. The key features of the app include:

- user registration and management: The application allows users to register, update their profiles, and reset their passwords via email with a token.

- transaction management: users can add, edit, delete, and view their financial transactions. Transactions are tied to the logged-in user, and the app supports both income and expenses.

- balance calculation: the app automatically calculates the user's balance based on their transactions, showing total income, expenses, and the current balance.

- security: endpoints are secured and only accessible to authenticated users, ensuring data privacy and security.

- unit tests: the app includes unit tests that verify key functionalities, such as user registration, transaction operations, and password reset processes.

For API testing, I used both automated unit tests with Django's TestCase, APITestCase and manual tests using Postman to ensure comprehensive coverage
In the application, Mailtrap.io was used to test the email sending functionality, allowing for a safe verification of whether the system correctly handles various email-related scenarios, without the risk of sending test messages to real users.