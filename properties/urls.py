from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('properties/', views.property_list_view, name='property_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # مسارات إدارة العقارات
    path('property/add/', views.property_create_view, name='property_add'),
    path('property/<int:pk>/edit/', views.property_update_view, name='property_edit'),
    path('property/<int:pk>/delete/', views.property_delete_view, name='property_delete'),
    
    # مسارات العقود
    path('contract/add/', views.contract_create_view, name='contract_add'),
    path('expense/add/', views.expense_create_view, name='expense_add'),
    path('installment/<int:pk>/pay/', views.pay_installment_view, name='installment_pay'),
    
]