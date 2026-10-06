
from django import forms

from products.models import Product
from .models import StockMovement


class StockMovementForm(forms.Form):

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    movement_type = forms.ChoiceField(
        choices=StockMovement.MovementType.choices,
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    quantity = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.01",
            "min": "0.01",
            "placeholder": "Enter quantity",
        }),
    )

    reference = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Invoice number or reference",
        }),
    )

    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Reason for this movement",
        }),
    )