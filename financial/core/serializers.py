from rest_framework import serializers
from .models import FinancialDataModel


class FinancialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialDataModel
        fields = ("id", "symbol", "date", "open_price", "close_price", "volume")
