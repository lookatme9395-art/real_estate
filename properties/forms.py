from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('CLIENT', 'مستأجر / بحث عن عقار'),
        ('OWNER', 'مالك / وسيط عقاري (إضافة عقارات)'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='نوع الحساب',
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role')
        
        # منح صلاحية الإضافة للمالك أو الموظف في الشركات الحقيقية
        if user.role in ['OWNER', 'STAFF']:
            user.is_staff = True

        if commit:
            user.save()
        return user


class PropertyForm(forms.ModelForm):

  class Meta:
    model = Property
    fields = [
        'title',
        'description',
        'listing_type',
        'status',
        'price',
        'area',
        'address',
    ]
    widgets = {
        'title': forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2'
                ' focus:ring-blue-500'
            }
        ),
        'description': forms.Textarea(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                ),
                'rows': 4,
            }
        ),
        'listing_type': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'status': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'price': forms.NumberInput(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'area': forms.NumberInput(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'address': forms.Textarea(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                ),
                'rows': 2,
            }
        ),
    }


class ContractForm(forms.ModelForm):

  class Meta:
    model = Contract
    fields = [
        'property',
        'client',
        'contract_type',
        'payment_system',
        'start_date',
        'end_date',
        'total_amount',
    ]
    widgets = {
        'property': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'client': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'contract_type': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'payment_system': forms.Select(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
        'start_date': forms.DateInput(
            attrs={
                'type': 'date',
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                ),
            }
        ),
        'end_date': forms.DateInput(
            attrs={
                'type': 'date',
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                ),
            }
        ),
        'total_amount': forms.NumberInput(
            attrs={
                'class': (
                    'w-full px-4 py-2 border rounded-lg focus:ring-2'
                    ' focus:ring-blue-500'
                )
            }
        ),
    }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['property', 'expense_type', 'amount', 'date', 'description']
        widgets = {
            'property': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'expense_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
        }