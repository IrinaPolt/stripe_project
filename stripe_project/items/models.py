from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Item(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    stripe_product_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название налога')
    rate = models.FloatField(
        verbose_name='Размер налога')

    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'

    def __str__(self):
        return f'{self.name} в штате Техас: {self.rate}%'

    def get_display_tax(self):
        return self.rate


class Discount(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название скидки')
    size = models.IntegerField(
        verbose_name='Размер скидки')
    stripe_coupon_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f'{self.name}: {self.size}%'

    def get_display_tax(self):
        return self.size


class Price(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='Товар')
    stripe_price_id_usd = models.CharField(max_length=100)
    stripe_price_id_eur = models.CharField(max_length=100)
    price_usd = models.IntegerField(
        default=0,
        verbose_name='Цена в долларах')
    price_eur = models.IntegerField(
        default=0,
        verbose_name='Цена в евро')
    tax = models.ForeignKey(
        Tax,
        on_delete=models.DO_NOTHING,
        verbose_name='Налог')
    discount = models.ForeignKey(
        Discount,
        on_delete=models.DO_NOTHING,
        verbose_name='Скидка',
        blank=True,
    )

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def get_display_price_usd(self):
        return "{0:.2f}".format(self.price_usd / 100)

    def get_display_price_eur(self):
        return "{0:.2f}".format(self.price_eur / 100)


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель')
    prices = models.ManyToManyField(
        Price,
        verbose_name='Цены в заказе',
        through='PriceInOrder',
        related_name='orders'
    )
    total_usd = models.IntegerField(default=0)
    total_eur = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class PriceInOrder(models.Model):
    """Вспомогательная модель для сбора заказа из нескольких товаров."""
    price = models.ForeignKey(
        Price,
        verbose_name='Цена',
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=0)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return self.price.item.name

    def get_cost_usd(self):
        return "{0:.2f}".format(self.price.price_usd * self.quantity / 100)

    def get_cost_eur(self):
        return "{0:.2f}".format(self.price.price_eur * self.quantity / 100)
