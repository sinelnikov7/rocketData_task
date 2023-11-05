from django.utils import timezone
from rest_framework import serializers

from .models import Product, Employee, NetworkNode


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор создания и получения продуктов"""
    class Meta:
        model = Product
        fields = '__all__'


class ProductUpdateSerializer(ProductSerializer):
    """Сериализатор обновления продуктов"""
    name = serializers.CharField(max_length=25, required=False)
    model = serializers.CharField(max_length=255, required=False)
    date_release = serializers.DateField(required=False)
    def validate_date_release(self, value):
        """Проверка корректности даты выхода продукта на рынок. Дата не должна быть в будущем."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Дата выхода продукта не может быть в будущем.")
        return value

class EmploeeSerializer(serializers.ModelSerializer):
    """Сериализатор сотрудников"""
    class Meta:
        model = Employee
        fields = '__all__'


class FulNetworkSerializer(serializers.ModelSerializer):
    """Сериализатор для получение полного бъекта торговой сети"""
    products = ProductSerializer(many=True)
    employees = EmploeeSerializer(many=True)

    class Meta:
        model = NetworkNode
        fields = '__all__'
        depth = 5

    def to_representation(self, instance):
        """Настройка порядка отображения полей в Json"""
        representation = super().to_representation(instance)
        response = {}
        previous_value = None
        def rec(dict):
            """Установка порядка вывода полей объекта перед отправкой для удобства чтения json"""
            nonlocal response
            nonlocal previous_value
            if dict.get('supplier') != None:
                rec(dict.get('supplier'))
            response = {
                "id": dict.get('id'),
                "type": dict.get('type'),
                "name": dict.get('name'),
                "email": dict.get('email'),
                "country": dict.get('country'),
                "city": dict.get('city'),
                "street": dict.get('street'),
                "house_number": dict.get('house_number'),
                "debt": dict.get('debt'),
                "created_at": dict.get('created_at'),
                "network_endpoint": dict.get('network_endpoint'),
                "products": dict.get('products'),
                "employees": dict.get('employees'),
                "supplier": previous_value,
            }
            previous_value = response
        rec(representation)
        return response

class PartNetworkSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и получени бъекта звена торговой сети"""
    network_endpoint = serializers.BooleanField(read_only=True)

    class Meta:
        model = NetworkNode
        exclude = ('author', )

    def validate(self, data):
        '''Валидация иерархии при создании и редактировании объектов через api'''
        org_type = ['Завод', 'Дистрибьютор', 'Дилерский центр', 'Крупная розничная сеть',
                    'Индивидуальный предприниматель']
        type = data.get('type')
        supplier = data.get('supplier')
        type_suplier = None
        if supplier:
            type_suplier = supplier.type
        data.pop('network_endpoint', None)
        if type_suplier and type:
            if int(type) == 0 and supplier is not None:
                raise serializers.ValidationError({'supplier': ["У типа завод нельзя выбрать поставщика"]})
            if int(type) == int(type_suplier):
                raise serializers.ValidationError({'supplier': [f'Вы не можете выбрать тип поставщика {org_type[int(type_suplier)]} в качестве'
                                          f' поставщика для организации типа {org_type[int(type)]}']})
            if int(type) < int(type_suplier):
                raise serializers.ValidationError( {'supplier': [f'Тип поставщика должен быть выше по иерархии чем выбранный тип организации']})
        if int(type) > 0 and type_suplier == None:
            raise serializers.ValidationError(
                {'supplier': [f'У всех типов организаций кроме завода должен быть поставщик. Необходимо выбрать поставщика']})
        return data


class PartNetworkUpdateSerializer(PartNetworkSerializer):
    """Сериализатор для обновления бъекта звена торговой сети"""
    type = serializers.ChoiceField(choices=NetworkNode.TYPE_CHOICES, required=False)
    name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    country = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=100, required=False)
    street = serializers.CharField(max_length=100, required=False)
    house_number = serializers.CharField(max_length=50, required=False)
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), required=False)
    employees = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all(), required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=NetworkNode.objects.all(), required=False, allow_null=True)
    debt = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    network_endpoint = serializers.BooleanField(read_only=True)