import django_filters

from .models import NetworkNode


class NetworkFilter(django_filters.FilterSet):
    '''Фильтр звеньев торговой цепи'''
    country = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по полю "Текст"')
    product = django_filters.CharFilter(method='filter_by_product')

    class Meta:
        model = NetworkNode
        fields = ['country', 'product']

    def filter_by_product(self, queryset, name, value):
        return queryset.filter(products__id=value)