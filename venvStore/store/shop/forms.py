from django import forms
from .models import CartItem


class CartItemForm(forms.ModelForm):
    """форма добавления товара"""
    class Meta:
        model = CartItem
        fields = ('quantity',)