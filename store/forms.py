"""
Forms for the store app.
"""
from django import forms

from django.contrib.auth.models import User
from .models import Order, Vendor, Review, Profile

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




class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user personal details.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        """Meta definition for UserUpdateForm."""
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating extended profile details.
    """
    class Meta:
        """Meta definition for ProfileUpdateForm."""
        model = Profile
        fields = ['shop_name', 'gst_number', 'address', 'city', 'state', 'pincode']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
        }
