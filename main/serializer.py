from rest_framework import serializers

from .models import Product, Employee, NetworkNode


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class EmploeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'


class NetworkSerializer(serializers.ModelSerializer):

    products = ProductSerializer(many=True)
    employees = EmploeeSerializer(many=True)

    class Meta:
        model = NetworkNode
        # fields = '__all__'
        fields = ('id', 'type', 'name', 'email', 'country', 'city', 'street', 'house_number', 'debt', 'created_at',
                  'network_endpoint', 'products', 'employees', 'supplier',)
        depth = 5
