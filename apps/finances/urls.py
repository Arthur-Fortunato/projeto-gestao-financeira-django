from django.urls import path
from . import views

app_name = "finances"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("receitas/", views.incomes, name="incomes"),
    path("receitas/excluir/<int:income_id>/", views.delete_income, name="delete_income"),
    path("despesas/", views.expenses, name="expenses"),
    path("despesas/excluir/<int:expense_id>/", views.delete_expense, name="delete_expense"),
    path("categorias/", views.categories, name="categories"),
    path("categorias/excluir/<int:category_id>/", views.delete_category, name="delete_category"),
    path("metas/", views.goals, name="goals"),
    path("metas/editar/<int:goal_id>/", views.update_goal, name="update_goal"),
    path("metas/excluir/<int:goal_id>/", views.delete_goal, name="delete_goal"),
    path("logout/", views.logout_view, name="logout"),
]
