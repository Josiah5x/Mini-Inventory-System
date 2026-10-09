
from django import forms
from django.forms import inlineformset_factory

from products.models import Product
from .models import OrderDocument, OrderItem


class OrderDocumentForm(forms.ModelForm):
    class Meta:
        model = OrderDocument
        fields = [
            "doc_code",
            "doc_year",
            "doc_num",
            "doc_date",
            "supplier",
            "supplier_name",
            "supplier_invoice",
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
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
            "tax": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.DateInput):
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs["class"] = "form-select"
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs["class"] = "form-control"
                else:
                    field.widget.attrs["class"] = "form-control"

        if "supplier" in self.fields:
            self.fields["supplier"].required = False
            self.fields["supplier"].queryset = (
                self.fields["supplier"].queryset.filter(is_active=True)
            )

        if "customer" in self.fields:
            self.fields["customer"].required = False
            self.fields["customer"].queryset = (
                self.fields["customer"].queryset.filter(is_active=True)
            )


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            "product",
            "warehouse",
            "product_qty",
            "product_price",
            "percentage_discount",
        ]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "warehouse": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Warehouse / location",
            }),
            "product_qty": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
            }),
            "product_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
            "percentage_discount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "max": "100",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["product"].required = True

    def clean_product_qty(self):
        quantity = self.cleaned_data.get("product_qty")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_percentage_discount(self):
        discount = self.cleaned_data.get("percentage_discount")
        if discount is not None and not 0 <= discount <= 100:
            raise forms.ValidationError(
                "Discount must be between 0 and 100."
            )
        return discount


OrderItemFormSet = inlineformset_factory(
    OrderDocument,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)