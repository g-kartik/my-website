from django import forms
from .models import MyStocks


class StockForm(forms.ModelForm):
    class Meta:
        model = MyStocks
        fields = ['ticker', 'user']