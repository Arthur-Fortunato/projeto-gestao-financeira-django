from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .forms import *
from decimal import Decimal, InvalidOperation
from django.db.models import Sum

@login_required
def dashboard(request):
    total_incomes = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = total_incomes - total_expenses
    
    recent_incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'total_incomes': total_incomes,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_incomes': recent_incomes,
        'goals': goals,
    }
    return render(request, "finances/pages/dashboard.html", context)

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

@login_required
def goals(request):
    if request.method == "POST":
        title = request.POST.get("title")
        target_amount = request.POST.get("target_amount")
        current_amount = request.POST.get("current_amount") or "0"
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        try:
            target_amount = Decimal(target_amount)
            current_amount = Decimal(current_amount)
        except (InvalidOperation, TypeError):
            messages.error(request, "Informe valores numéricos válidos.")
            return redirect("finances:goals")

        if target_amount < 0 or current_amount < 0:
            messages.error(request, "Os valores não podem ser negativos.")
            return redirect("finances:goals")

        if start_date and end_date and start_date > end_date:
            messages.error(request, "A data final deve ser maior que a data inicial.")
            return redirect("finances:goals")

        Goal.objects.create(
            user=request.user,
            title=title,
            target_amount=target_amount,
            current_amount=current_amount,
            start_date=start_date or None,
            end_date=end_date or None,
        )
        messages.success(request, "Meta criada com sucesso.")
        return redirect("finances:goals")

    goals = Goal.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "finances/pages/goals.html", {
        "goals": goals,
    })
    
@login_required
def update_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == "POST":
        value = request.POST.get("current_amount")
        try:
            value = Decimal(value)
        except (InvalidOperation, TypeError):
            messages.error(request, "Informe um valor válido.")
            return redirect("finances:goals")

        if value <= 0:
            messages.error(request, "Informe um valor maior que zero.")
            return redirect("finances:goals")

        goal.current_amount += value
        goal.save()

        messages.success(request, "Meta atualizada com sucesso.")
    return redirect("finances:goals")

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == "POST":
        goal.delete()
    return redirect("finances:goals")