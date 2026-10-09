
from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "phone",
            "email",
            "address",
            "opening_balance",
            "credit_limit",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Customer or business name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "opening_balance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "credit_limit": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_credit_limit(self):
        value = self.cleaned_data["credit_limit"]
        if value < 0:
            raise forms.ValidationError(
                "Credit limit cannot be negative."
            )
        return value