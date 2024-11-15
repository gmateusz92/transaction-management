from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    # Pobieramy transakcje dla zalogowanego użytkownika
    transactions = Transaction.objects.filter(user=request.user)
    serializer = TransactionSerializer(transactions, many=True)
    return Response({"transactions": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_transaction(request):
    user = request.user

    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)  # Automatycznie przypisujemy użytkownika
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_transaction(request, pk):
    # Pobieramy transakcję
    transaction = get_object_or_404(Transaction, id=pk)

    # Sprawdzamy, czy użytkownik ma prawo do edycji
    if transaction.user != request.user:
        raise PermissionDenied("You do not have permission to edit this transaction.")

    # Deserializacja danych
    serializer = TransactionSerializer(transaction, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_transaction(request, pk):
    # Pobieramy transakcję
    transaction = get_object_or_404(Transaction, id=pk)

    # Sprawdzamy, czy użytkownik ma prawo do usunięcia
    if transaction.user != request.user:
        raise PermissionDenied("You do not have permission to delete this transaction.")

    # Usunięcie transakcji
    transaction.delete()
    return Response(
        {"detail": "Transaction deleted successfully"},
        status=status.HTTP_204_NO_CONTENT,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_balance(request):
    user = request.user
    income = (
        Transaction.objects.filter(user=user, transaction_type="income").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
    expenses = (
        Transaction.objects.filter(user=user, transaction_type="expense").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
    balance = income - expenses
    return Response({"income": income, "expenses": expenses, "balance": balance})
