from django import forms

from products.models import Product
from suppliers.models import Supplier

from .models import Purchase, PurchaseItem


from django.utils import timezone

class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        fields = [
            "invoice_number",
            "supplier",
            "purchase_date",
            "discount",
            "note",
        ]

        widgets = {
            "invoice_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. INV-0001",
                }
            ),

            "supplier": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "purchase_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional purchase note...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["purchase_date"].initial = timezone.localdate()

class PurchaseItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseItem

        fields = [
            "product",
            "quantity",
            "unit_cost",
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select",
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
            }),

            "unit_cost": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
        }