from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .forms import *

@login_required
def dashboard(request):
    return render(request, "finances/pages/dashboard.html")

@login_required
def incomes(request):
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        object_type = request.POST.get("object_type")

        if object_type == "income" and object_id:
            income = get_object_or_404(Income, id=object_id, user=request.user)
            form = IncomeForm(request.POST, instance=income, user=request.user)
        else:
            form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect("finances:incomes")
    else:
        form = IncomeForm(user=request.user)

    incomes = Income.objects.filter(user=request.user).order_by("-date")
    return render(request, "finances/pages/incomes.html", {
        "form": form,
        "incomes": incomes,
    })
    
@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    if request.method == "POST":
        income.delete()
    return redirect("finances:incomes")

@login_required
def expenses(request):
    if request.method == "POST":
        object_id = request.POST.get("object_id")
        object_type = request.POST.get("object_type")
        if object_type == "expense" and object_id:
            expense = get_object_or_404(Expense, id=object_id, user=request.user)
            form = ExpenseForm(request.POST, instance=expense, user=request.user)
        else:
            form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("finances:expenses")
    else:
        form = ExpenseForm(user=request.user)
    
    expenses = Expense.objects.filter(user=request.user).order_by("-date")
    return render(request, "finances/pages/expenses.html", {
        "form": form,
        "expenses": expenses,
    })
    
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
    return redirect("finances:expenses")

@login_required
def categories(request):
    if request.method == "POST":
        name = request.POST.get("name")
        type = request.POST.get("type")
        if name and type:
            try:
                Category.objects.create(name=name, type=type, user=request.user)
                messages.success(request, "Categoria criada com sucesso!")
            except IntegrityError:
                messages.error(request, "Essa categoria já existe.")
            return redirect("finances:categories")
    categories = Category.objects.filter(user=request.user)
    return render(request, "finances/pages/categories.html", {
        "categories": categories
    })
    
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == "POST":
        category.delete()

    return redirect("finances:categories")

def logout_view(request):
    logout(request)
    return redirect("landing:index")