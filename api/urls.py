from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.get_transactions, name='get-transactions'),
    path('transactions/add/', views.add_transaction, name='add-transaction'),
    path('transactions/<int:pk>/edit/', views.update_transaction, name='update-transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction, name='delete-transaction'),
    path('transactions/balance/', views.get_balance, name='get-balance'),
]
