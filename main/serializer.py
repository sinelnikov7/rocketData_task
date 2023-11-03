from rest_framework import serializers

from .models import Product, Employee, NetworkNode


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продуктов"""
    class Meta:
        model = Product
        fields = '__all__'


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
    """Сериализатор для получение бъекта звена торговой сети"""
    network_endpoint = serializers.BooleanField(read_only=True)
    # debt = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = NetworkNode
        fields = '__all__'

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