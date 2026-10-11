
from django import forms

from documents.models import OrderDocument
from documents.forms import OrderItemForm, OrderItemFormSet


class SaleDocumentForm(forms.ModelForm):
    """Customer and transaction details for a sales invoice."""

    class Meta:
        model = OrderDocument
        fields = [
            "doc_date",
            "customer",
            "customer_name",
            "currency",
            "credit_fercility",
            "address",
            "project",
            "tax",
        ]
        widgets = {
            "doc_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),
            "customer": forms.Select(attrs={
                "class": "form-select",
            }),
            "customer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Customer name for a walk-in sale",
            }),
            "currency": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "NGN",
            }),
            "credit_fercility": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Cash, credit, bank transfer, etc.",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Customer address",
            }),
            "project": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional project or reference",
            }),
            "tax": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["customer"].required = False
        self.fields["customer"].queryset = (
            self.fields["customer"].queryset.filter(is_active=True)
        )
        self.fields["tax"].min_value = 0

    def clean_tax(self):
        tax = self.cleaned_data.get("tax")

        if tax is not None and tax < 0:
            raise forms.ValidationError(
                "Tax cannot be negative."
            )

        return tax
