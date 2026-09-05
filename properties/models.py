from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'مدير النظام (الأدمن)'
        STAFF = 'STAFF', 'موظف شركة'
        CLIENT = 'CLIENT', 'عميل'
        OWNER = 'OWNER', 'مالك / وسيط عقاري'

    role = models.CharField(
        choices=Role.choices, default=Role.CLIENT, max_length=20
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

# (باقي النماذج Property, PropertyImage, Contract, Installment, Expense تبقى كما هي بدون تغيير)


# 2. نموذج العقار الأساسي
class Property(models.Model):

  class ListingType(models.TextChoices):
    COMPANY_ASSET = 'ASSET', 'ملكية خاصة للشركه'
    FOR_SALE = 'SALE', 'للبيع'
    FOR_RENT = 'RENT', 'للإيجار'

  class PropertyStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'متاح'
    RENTED = 'RENTED', 'مؤجر'
    SOLD = 'SOLD', 'مباع'
    UNDER_MAINTENANCE = 'MAINTENANCE', 'تحت الصيانة'

  title = models.CharField(max_length=200, verbose_name='عنوان العقار')
  description = models.TextField(verbose_name='التفاصيل')
  listing_type = models.CharField(
      choices=ListingType.choices, max_length=20, verbose_name='نوع العرض'
  )
  status = models.CharField(
      choices=PropertyStatus.choices,
      default=PropertyStatus.AVAILABLE,
      max_length=20,
      verbose_name='حالة العقار',
  )
  price = models.DecimalField(
      max_digits=12, decimal_places=2, verbose_name='السعر / قيمة الإيجار'
  )
  area = models.DecimalField(
      max_digits=8, decimal_places=2, verbose_name='المساحة (متر مربع)'
  )
  address = models.TextField(verbose_name='العنوان بالتفصيل')

  owner = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      related_name='properties',
      verbose_name='المسؤول / المالك',
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.title} - {self.get_listing_type_display()}'


# 3. نموذج صور العقار
class PropertyImage(models.Model):
  property = models.ForeignKey(
      Property,
      on_delete=models.CASCADE,
      related_name='images',
      verbose_name='العقار',
  )
  image = models.ImageField(
      upload_to='properties/images/', verbose_name='صورة العقار'
  )
  is_main = models.BooleanField(default=False, verbose_name='صورة رئيسية')

  def __str__(self):
    return f'صورة لـ {self.property.title}'


# 4. نموذج العقود
class Contract(models.Model):

  class ContractType(models.TextChoices):
    SALE = 'SALE', 'عقد بيع'
    RENT = 'RENT', 'عقد إيجار'

  class PaymentSystem(models.TextChoices):
    MONTHLY = 'MONTHLY', 'شهري'
    QUARTERLY = '4_INSTALLMENTS', '4 دفعات (ربع سنوي)'
    SEMI_ANNUAL = '6_INSTALLMENTS', '6 دفعات (كل شهرين)'
    LUMP_SUM = 'LUMP_SUM', 'دفعة واحدة'

  property = models.ForeignKey(
      Property, on_delete=models.PROTECT, verbose_name='العقار المتعاقد عليه'
  )
  client = models.ForeignKey(
      User,
      on_delete=models.PROTECT,
      related_name='contracts',
      verbose_name='العميل',
  )
  created_by = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      related_name='created_contracts',
      verbose_name='الموظف المسؤول',
  )
  contract_type = models.CharField(
      choices=ContractType.choices, max_length=10, verbose_name='نوع العقد'
  )
  payment_system = models.CharField(
      choices=PaymentSystem.choices,
      default=PaymentSystem.MONTHLY,
      max_length=20,
      verbose_name='نظام الدفع',
  )
  start_date = models.DateField(verbose_name='تاريخ البداية')
  end_date = models.DateField(
      blank=True, null=True, verbose_name='تاريخ النهاية'
  )
  total_amount = models.DecimalField(
      max_digits=12, decimal_places=2, verbose_name='إجمالي المبلغ'
  )
  is_active = models.BooleanField(default=True, verbose_name='العقد ساري')

  def __str__(self):
    return (
        f'عقد {self.get_contract_type_display()} - {self.property.title}'
    )


# 5. نموذج الأقساط المالية
class Installment(models.Model):

  class Status(models.TextChoices):
    PENDING = 'PENDING', 'معلق (غير مدفوع)'
    PAID = 'PAID', 'تم الدفع'
    OVERDUE = 'OVERDUE', 'متأخر'

  contract = models.ForeignKey(
      Contract,
      on_delete=models.CASCADE,
      related_name='installments',
      verbose_name='العقد المرتبط',
  )
  amount = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name='مبلغ القسط'
  )
  due_date = models.DateField(verbose_name='تاريخ استحقاق القسط')
  status = models.CharField(
      choices=Status.choices,
      default=Status.PENDING,
      max_length=20,
      verbose_name='حالة الدفع',
  )
  paid_date = models.DateField(
      blank=True, null=True, verbose_name='تاريخ السداد الفعلي'
  )

  def __str__(self):
    return (
        f'قسط بقيمة {self.amount} - استحقاق: {self.due_date} ({self.get_status_display()})'
    )

class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('MAINTENANCE', 'صيانة'),
        ('ELECTRICITY', 'كهرباء'),
        ('WATER', 'مياه'),
        ('OTHER', 'أخرى'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES, verbose_name="نوع المصروف")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    date = models.DateField(verbose_name="تاريخ الفاتورة")
    description = models.TextField(verbose_name="ملاحظات")
    
    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.property.title}"