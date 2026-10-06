from django import forms

from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Supplier name",
            }),
            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contact person",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "08012345678",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "supplier@example.com",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Supplier address",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }