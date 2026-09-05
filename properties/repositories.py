from .models import Contract, Property


class PropertyRepository:
  """مسؤول عن جلب واستعلامات العقارات من قاعدة البيانات"""

  @staticmethod
  def get_all_properties():
    return Property.objects.all().order_by('-created_at')

  @staticmethod
  def get_property_by_id(property_id):
    try:
      return Property.objects.get(id=property_id)
    except Property.DoesNotExist:
      return None

  @staticmethod
  def filter_properties(listing_type=None, status=None):
    queryset = Property.objects.all()
    if listing_type:
      queryset = queryset.filter(listing_type=listing_type)
    if status:
      queryset = queryset.filter(status=status)
    return queryset


class ContractRepository:
  """مسؤول عن استعلامات العقود والماليات"""

  @staticmethod
  def get_active_contracts():
    return Contract.objects.filter(is_active=True)

  @staticmethod
  def create_contract(data, user, property_obj):
    return Contract.objects.create(
        property=property_obj,
        client=data['client'],
        created_by=user,
        contract_type=data['contract_type'],
        start_date=data['start_date'],
        end_date=data.get('end_date'),
        total_amount=data['total_amount'],
    )