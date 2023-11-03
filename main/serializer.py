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


class NetworkSerializer(serializers.ModelSerializer):
    """Сериализатор торговой сети"""
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