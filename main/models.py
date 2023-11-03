from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class NetworkNode(models.Model):
    '''Модель звена сети'''
    TYPE_CHOICES = (
        ("0", 'Завод'),
        ("1", 'Дистрибьютор'),
        ("2", 'Дилерский центр'),
        ("3", 'Крупная розничная сеть'),
        ("4", 'Индивидуальный предприниматель'),
    )

    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='Тип организации')
    name = models.CharField(max_length=255, verbose_name='Название организации')
    email = models.EmailField(verbose_name='Электронный адрес')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house_number = models.CharField(max_length=50, verbose_name='Номер дома')
    products = models.ManyToManyField('Product', verbose_name='Продукты', related_name='network')
    employees = models.ManyToManyField('Employee', verbose_name='Сотрудники', related_name='network')
    supplier = models.ForeignKey('NetworkNode', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Поставщик')
    debt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Задолженность', default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    network_endpoint = models.BooleanField(default=True, verbose_name='Конечная точка сети')

    class Meta:
        verbose_name = "Звено сети по продаже электроники."
        verbose_name_plural = "Звенья сети по продаже электроники."

    def __str__(self):
        return f"{self.get_type_display()} - {self.name} id - {self.pk}"

    def clean(self):
        '''Валидация иерархии'''
        if self.supplier and self.type:
            '''У выбранного типа при создании в качестве поставщика нельзя выбрать такой же тип'''
            if self.type == self.supplier.type:
                raise ValidationError(f'Вы не можете выбрать {self.get_type_display()} в качестве'
                                      f' поставщика для организации типа {self.get_type_display()}')
            '''У типа завод нельзя выбрать поставщика'''
            if int(self.type) == 0 and self.supplier.type != None:
                raise ValidationError(f'У организации типа завод не может быть поставщика')
            '''В качестве поставщика можно выбрать только тип который выше по иерархии'''
            if int(self.type) < int(self.supplier.type):
                raise ValidationError(f'Тип поставщика должен быть выше по иерархии чем выбранный тип организации')
        '''Обязательный выбор поставщика если тип выбраной организации это не завод'''
        if int(self.type) > 0 and self.supplier == None:
            raise ValidationError(f'У всех типов организаций кроме завода должен быть поставщик.'
                                  f' Необходимо выбрать поставщика')


class Product(models.Model):
    '''Модель товаров'''
    name = models.CharField(max_length=255, verbose_name='Название товара')
    model = models.CharField(max_length=255, verbose_name='Модель товара')
    date_release = models.DateField(verbose_name='Дата выхода продукта на рынок')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Список товаров'

    def __str__(self):
        return f'{self.name} {self.model}'


class Employee(models.Model):
    '''Модель сотрудников'''
    name = models.CharField(max_length=255, verbose_name='Имя')
    surname = models.CharField(max_length=255, verbose_name='Фамилия')
    position = models.CharField(max_length=255, verbose_name='Должность')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.name} {self.surname} - {self.position}'


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(verbose_name="Адрес электронной почты", unique=True)
    is_active = models.BooleanField(default=True, verbose_name='Активный пользователь')

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} {self.email}"


@receiver(post_save, sender=NetworkNode)
def create_setting(sender, instance, **kwargs):
    """Снятие пометки конечной точки сети если объект выбран в качестве поставщика"""
    if instance.supplier:
        obj = instance.supplier
        obj.network_endpoint = False
        obj.save()
