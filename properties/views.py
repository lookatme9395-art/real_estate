from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import *
from .forms import *
from .repositories import PropertyRepository
from .services import ContractService


def index_view(request):
    """صفحة البداية الرئيسية"""
    latest_properties = Property.objects.filter(
        status=Property.PropertyStatus.AVAILABLE
    ).order_by('-created_at')[:3]
    return render(request, 'properties/index.html', {'latest_properties': latest_properties})


def register_view(request):
    """صفحة تسجيل حساب جديد"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'properties/register.html', {'form': form})


def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(email=email).first() or User.objects.filter(username=email).first()
        
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'كلمة المرور غير صحيحة'
        else:
            error = 'البريد الإلكتروني أو اسم المستخدم غير مسجل'

        return render(request, 'properties/login.html', {'error': error})

    return render(request, 'properties/login.html')


@login_required(login_url='login')
def dashboard_view(request):
    """لوحة التحكم المركزية مع عزل كامل للبيانات حسب دور المستخدم"""
    user = request.user
    context = {}

    # 1. لوحة إدارة الشركة (الأدمن والموظفين فقط)
    if user.role in ['ADMIN', 'STAFF'] or user.is_staff:
        context['properties'] = Property.objects.all().order_by('-created_at')
        context['contracts'] = Contract.objects.all().order_by('-start_date')
        context['expenses'] = Expense.objects.all().order_by('-date')

        total_income = Contract.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        context['net_profit'] = total_income - total_expenses
        
        template_name = 'properties/staff_dashboard.html'

    # 2. لوحة تحكم مالك العقار (عقاراته، عقوده، وأرباحه الخاصة فقط)
    elif user.role == 'OWNER':
        owner_properties = Property.objects.filter(owner=user)
        context['properties'] = owner_properties
        context['contracts'] = Contract.objects.filter(property__in=owner_properties)
        context['expenses'] = Expense.objects.filter(property__in=owner_properties)
        
        total_income = Contract.objects.filter(property__in=owner_properties).aggregate(total=Sum('total_amount'))['total'] or 0
        total_expenses = Expense.objects.filter(property__in=owner_properties).aggregate(total=Sum('amount'))['total'] or 0
        
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        context['net_profit'] = total_income - total_expenses
        
        template_name = 'properties/owner_dashboard.html'

    # 3. لوحة تحكم العميل / المستأجر (عقوده وأقساطه فقط)
    else:
        context['contracts'] = Contract.objects.filter(client=user)
        template_name = 'properties/client_dashboard.html'

    return render(request, template_name, context)


def property_list_view(request):
    """عرض قائمة العقارات"""
    properties = PropertyRepository.get_all_properties()
    return render(request, 'properties/property_list.html', {'properties': properties, 'title': 'قائمة العقارات'})


@login_required
def property_create_view(request):
    """إضافة عقار جديد"""
    if request.user.role == 'CLIENT':
        return redirect('dashboard')
    if request.user.role not in ['ADMIN', 'STAFF', 'OWNER'] and not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            return redirect('dashboard')
    else:
        form = PropertyForm()

    return render(request, 'properties/property_form.html', {'form': form, 'title': 'إضافة عقار جديد'})


@login_required
def property_update_view(request, pk):
    """تعديل بيانات العقار"""
    if request.user.role == 'CLIENT':
        return redirect('dashboard')
        
    prop = get_object_or_404(Property, pk=pk)
    if request.user.role not in ['ADMIN', 'STAFF'] and prop.owner != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PropertyForm(instance=prop)

    return render(request, 'properties/property_form.html', {'form': form, 'title': 'تعديل بيانات العقار'})


@login_required
def property_delete_view(request, pk):
    """حذف عقار"""
    if request.user.role == 'CLIENT':
        return redirect('dashboard')
        
    prop = get_object_or_404(Property, pk=pk)
    if request.user.role not in ['ADMIN', 'STAFF'] and prop.owner != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        prop.delete()
        return redirect('dashboard')

    return render(request, 'properties/property_confirm_delete.html', {'property': prop})


@login_required
def contract_create_view(request):
    """تسجيل عقد جديد وتوليد الأقساط"""
    if request.user.role == 'CLIENT':
        return redirect('dashboard')
    if request.user.role not in ['ADMIN', 'STAFF', 'OWNER'] and not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract_data = form.cleaned_data
            property_obj = contract_data['property']
            try:
                ContractService.register_new_contract(contract_data, request.user, property_obj.id)
                return redirect('dashboard')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = ContractForm()

    return render(request, 'properties/contract_form.html', {'form': form, 'title': 'تسجيل عقد جديد'})


@login_required
def expense_create_view(request):
    """إضافة مصروف جديد"""
    if request.user.role == 'CLIENT':
        return redirect('dashboard')
    if request.user.role not in ['ADMIN', 'STAFF', 'OWNER'] and not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    return render(request, 'properties/expense_form.html', {'form': form, 'title': 'تسجيل مصروف جديد'})


@login_required
def pay_installment_view(request, pk):
    """تسجيل سداد قسط معين وتحويل حالته إلى مدفوع"""
    installment = get_object_or_404(Installment, pk=pk)
    
    if request.user.role not in ['ADMIN', 'STAFF'] and not request.user.is_staff:
        return redirect('dashboard')

    installment.status = Installment.Status.PAID
    installment.paid_date = timezone.now().date()
    installment.save()
    
    return redirect('dashboard')


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    return redirect('index')