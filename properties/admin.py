from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Contract, Installment, Property, PropertyImage, User


# 1. تخصيص عرض المستخدمين في لوحة التحكم
@admin.register(User)
class CustomUserAdmin(UserAdmin):
  list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'is_active')
  list_filter = ('role', 'is_staff', 'is_active')
  fieldsets = UserAdmin.fieldsets + (
      ('صلاحيات النظام العقاري', {'fields': ('role', 'phone')}),
  )
  add_fieldsets = UserAdmin.add_fieldsets + (
      ('صلاحيات النظام العقاري', {'fields': ('role', 'phone')}),
  )


# 2. إتاحة رفع وإدارة صور العقار مباشرة داخل شاشة العقار (Inline)
class PropertyImageInline(admin.TabularInline):
  model = PropertyImage
  extra = 3  # يسمح برفع 3 صور دفعة واحدة مع العقار


# 3. تخصيص عرض العقارات
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
  list_display = (
      'title',
      'listing_type',
      'status',
      'price',
      'area',
      'owner',
      'created_at',
  )
  list_filter = ('listing_type', 'status', 'created_at')
  search_fields = ('title', 'address', 'description')
  inlines = [PropertyImageInline]
  list_per_page = 20


# 4. تخصيص عرض الأقساط داخل شاشة العقد (Inline)
class InstallmentInline(admin.TabularInline):
  model = Installment
  extra = 0
  readonly_fields = ('due_date', 'amount')


# 5. تخصيص عرض العقود والمبيعات/الإيجارات
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
  list_display = (
      'property',
      'client',
      'contract_type',
      'payment_system',
      'total_amount',
      'is_active',
      'start_date',
  )
  list_filter = ('contract_type', 'payment_system', 'is_active', 'start_date')
  search_fields = ('property__title', 'client__username')
  inlines = [InstallmentInline]


# تسجيل نموذج الأقساط منفصلاً أيضاً للمتابعة السريعة
@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
  list_display = ('contract', 'amount', 'due_date', 'status', 'paid_date')
  list_filter = ('status', 'due_date')
  search_fields = ('contract__property__title', 'contract__client__username')