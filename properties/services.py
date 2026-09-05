from .repositories import ContractRepository, PropertyRepository
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # مكتبة دجانجو تدعمها لحساب الشهور
from .models import *


class PropertyService:
  """منطق الأعمال الخاص بالعقارات"""

  @staticmethod
  def change_property_status(property_id, new_status):
    prop = PropertyRepository.get_property_by_id(property_id)
    if prop:
      prop.status = new_status
      prop.save()
      return True
    return False



class ContractService:

  @staticmethod
  def generate_installments(contract):
    """خوارزمية توليد الأقساط تلقائياً بناءً على نظام الدفع المختار"""
    total = contract.total_amount
    start = contract.start_date

    # تحديد عدد الدفعات والفترة الزمنية بينها
    if contract.payment_system == 'MONTHLY':
      count = 12  # كمثال لسنة أو حسب العقد
      delta_months = 1
    elif contract.payment_system == '4_INSTALLMENTS':
      count = 4
      delta_months = 3  # كل 3 أشهر قسط
    elif contract.payment_system == '6_INSTALLMENTS':
      count = 6
      delta_months = 2  # كل شهرين قسط
    else:
      count = 1
      delta_months = 0

    installment_amount = total / count

    # إنشاء الأقساط في قاعدة البيانات
    for i in range(count):
      if delta_months == 0:
        due_date = start
      else:
        due_date = start + relativedelta(months=+(i * delta_months))

      Installment.objects.create(
          contract=contract,
          amount=installment_amount,
          due_date=due_date,
          status=Installment.Status.PENDING,
      )

  @staticmethod
  def register_new_contract(contract_data, staff_user, property_id):
    # (الخطوات السابقة للتحقق من العقار...)
    prop = PropertyRepository.get_property_by_id(property_id)
    if not prop or prop.status != Property.PropertyStatus.AVAILABLE:
      raise ValueError('هذا العقار غير متاح للتعاقد حالياً.')

    # 1. إنشاء العقد الأساسي
    contract = ContractRepository.create_contract(
        contract_data, staff_user, prop
    )

    # 2. توليد الأقساط المالية تلقائياً
    ContractService.generate_installments(contract)

    # 3. تحديث حالة العقار (مباع أو مؤجر)
    if contract.contract_type == Contract.ContractType.SALE:
      PropertyService.change_property_status(
          property_id, Property.PropertyStatus.SOLD
      )
    elif contract.contract_type == Contract.ContractType.RENT:
      PropertyService.change_property_status(
          property_id, Property.PropertyStatus.RENTED
      )

    return contract