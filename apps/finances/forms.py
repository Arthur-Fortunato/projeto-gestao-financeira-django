from django import forms
from .models import Expense, Income, Category, CategoryType

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["title", "amount", "category", "date", "is_fixed", "notes"]
        labels = {
            "title": "Título", 
            "amount": "Valor", 
            "category": "Categoria", 
            "date": "Data", 
            "is_fixed": "Receita é fixa?", 
            "notes": "Observações"
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user, type=CategoryType.INCOME)
            
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "amount", "category", "date", "is_fixed", "notes"]

        labels = {
            "title": "Título",
            "amount": "Valor",
            "category": "Categoria",
            "date": "Data",
            "is_fixed": "Receita é Fixa?",
            "notes": "Observações",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user, type=CategoryType.EXPENSE)