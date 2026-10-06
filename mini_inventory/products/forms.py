from django import forms
from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Electronics",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Category description...",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            "category",
            "name",
            "sku",
            "barcode",
            "description",
            "unit",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "minimum_stock",
            "image",
            "is_active",
        ]

        widgets = {
            "category": forms.Select(attrs={
                "class": "form-select",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Product name",
            }),

            "sku": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. PRD-001",
            }),

            "barcode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Barcode",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Product description...",
            }),

            "unit": forms.Select(attrs={
                "class": "form-select",
            }),

            "cost_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),

            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),

            "stock_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0",
                "step": "0.01",
                "min": "0",
            }),

            "minimum_stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "5",
                "step": "0.01",
                "min": "0",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }