import csv
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from .models import *
from .forms import *
from decimal import Decimal, InvalidOperation
from django.db.models import Sum


def parse_date(value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def get_default_period():
    today = datetime.date.today()
    return today.replace(day=1), today


@login_required
def dashboard(request):
    start_date = parse_date(request.GET.get('start_date'))
    end_date = parse_date(request.GET.get('end_date'))
    if not start_date or not end_date:
        start_date, end_date = get_default_period()

    categories = Category.objects.filter(user=request.user).order_by('name')
    selected_category = None
    category_id = request.GET.get('category')
    if category_id:
        selected_category = categories.filter(id=category_id).first()

    incomes = Income.objects.filter(user=request.user, date__range=(start_date, end_date))
    expenses = Expense.objects.filter(user=request.user, date__range=(start_date, end_date))
    if selected_category:
        incomes = incomes.filter(category=selected_category)
        expenses = expenses.filter(category=selected_category)

    total_incomes = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = total_incomes - total_expenses

    recent_incomes = incomes.order_by('-date')[:5]
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')

    income_by_month_formatted = {}
    expense_by_month_formatted = {}
    
    for item in incomes.values('date__year', 'date__month').annotate(total=Sum('amount')).order_by('date__year', 'date__month'):
        key = (item['date__year'], item['date__month'])
        income_by_month_formatted[key] = float(item['total'])
    
    for item in expenses.values('date__year', 'date__month').annotate(total=Sum('amount')).order_by('date__year', 'date__month'):
        key = (item['date__year'], item['date__month'])
        expense_by_month_formatted[key] = float(item['total'])

    date_labels = []
    incomes_series = []
    expenses_series = []
    
    current_month = start_date.replace(day=1)
    end_month = end_date.replace(day=1)
    
    while current_month <= end_month:
        month_key = (current_month.year, current_month.month)
        date_labels.append(current_month.strftime('%m/%Y'))
        incomes_series.append(income_by_month_formatted.get(month_key, 0))
        expenses_series.append(expense_by_month_formatted.get(month_key, 0))
        
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)

    category_data = {}
    category_types = {}
    
    for item in incomes.values('category__name').annotate(total=Sum('amount')).order_by('category__name'):
        name = item['category__name'] or 'Sem categoria'
        category_data[name] = category_data.get(name, 0) + float(item['total'])
        category_types[name] = 'income'
    
    for item in expenses.values('category__name').annotate(total=Sum('amount')).order_by('category__name'):
        name = item['category__name'] or 'Sem categoria'
        category_data[name] = category_data.get(name, 0) + float(item['total'])
        category_types[name] = 'expense'

    category_labels = []
    category_totals = []
    category_type_list = []
    
    for label in sorted(category_data.keys()):
        type_label = category_types.get(label, 'expense')
        type_text = 'receita' if type_label == 'income' else 'despesa'
        category_labels.append(f"{label} ({type_text})")
        category_totals.append(category_data[label])
        category_type_list.append(type_label)

    context = {
        'total_incomes': total_incomes,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_incomes': recent_incomes,
        'goals': goals,
        'categories': categories,
        'selected_category': selected_category,
        'start_date': start_date,
        'end_date': end_date,
        'date_labels': date_labels,
        'incomes_series': incomes_series,
        'expenses_series': expenses_series,
        'category_labels': category_labels,
        'category_totals': category_totals,
        'category_types': category_type_list,
    }
    return render(request, 'finances/pages/dashboard.html', context)


@login_required
def dashboard_export_csv(request):
    start_date = parse_date(request.GET.get('start_date'))
    end_date = parse_date(request.GET.get('end_date'))
    if not start_date or not end_date:
        start_date, end_date = get_default_period()

    categories = Category.objects.filter(user=request.user)
    selected_category = None
    category_id = request.GET.get('category')
    if category_id:
        selected_category = categories.filter(id=category_id).first()

    incomes = Income.objects.filter(user=request.user, date__range=(start_date, end_date))
    expenses = Expense.objects.filter(user=request.user, date__range=(start_date, end_date))
    if selected_category:
        incomes = incomes.filter(category=selected_category)
        expenses = expenses.filter(category=selected_category)

    rows = []
    for income in incomes.order_by('date'):
        rows.append([
            'Receita',
            income.date.isoformat(),
            f'{income.amount:.2f}',
            income.title,
            income.category.name if income.category else '',
            income.notes,
        ])
    for expense in expenses.order_by('date'):
        rows.append([
            'Despesa',
            expense.date.isoformat(),
            f'{expense.amount:.2f}',
            expense.title,
            expense.category.name if expense.category else '',
            expense.notes,
        ])
    rows.sort(key=lambda item: item[1])

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_mensal.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Tipo', 'Data', 'Valor', 'Título', 'Categoria', 'Observações'])
    writer.writerows(rows)

    return response


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