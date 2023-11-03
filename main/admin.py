from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import NetworkNode, Product, Employee, User


class NetworkNodeAdmin(admin.ModelAdmin):
    """Настройка админ панели для объектов сети"""
    filter_horizontal = ['products', 'employees']
    list_filter = ['city']
    search_fields = ['city']
    list_display = ['id', 'type', 'name', 'email', 'supplier_link', 'debt']
    actions = ['clear_debt']
    ordering = ['type']
    readonly_fields = ('network_endpoint',)

    def supplier_link(self, obj):
        '''Отображение ссылки на объект поставщика'''
        if obj.supplier:
            url = reverse("admin:main_networknode_change", args=[obj.supplier.id])
            return format_html(f'<a href="{url}">{obj.supplier}</a>')
        if int(obj.type) == 0:
            return "-"
        else:
            return format_html(f'<p style="color:red; padding-left:0">Поставщик не выбран</p>')

    supplier_link.short_description = 'Поставщик'

    @admin.action(description='Обнулить задолженность')
    def clear_debt(self, request, queryset):
        '''Действие позволяющее сбросить задолженность у выбранных объектов'''
        queryset.update(debt=0)
        self.message_user(request, 'Задолженность обнулена')

admin.site.register(NetworkNode, NetworkNodeAdmin)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(User)



