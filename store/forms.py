"""
Forms for the store app.
"""
from django import forms

from .models import Order, Vendor, Review

class OrderForm(forms.ModelForm):
    """
    Form for validating order details.
    """
    class Meta:
        """Meta definition for OrderForm."""
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'zipcode', 'place', 'phone']

class ReviewForm(forms.ModelForm):
    """
    Form for submitting product reviews and ratings.
    """
    rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label='Rating'
    )

    class Meta:
        """Meta definition for Review."""
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize your experience (optional)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your detailed review...'
            })
        }

class VendorRegistrationForm(forms.ModelForm):
    """
    Form for registering a new vendor.
    """
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """Meta definition for VendorRegistrationForm."""
        model = Vendor
        fields = ['name', 'city', 'logo']
