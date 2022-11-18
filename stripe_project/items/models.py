from django.db import models



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


class Price(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='Товар')
    stripe_price_id = models.CharField(max_length=100)
    price = models.IntegerField(
        default=0,
        verbose_name='Цена')

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)


class Order(models.Model):
    prices = models.ManyToManyField(
        Price,
        through='PriceInOrder',
        verbose_name='Цены',
        related_name='items_prices'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def get_full_price(self):
        full_price = 0
        for price in self.prices:
            full_price =+ price.price
        return "{0:.2f}".format(full_price / 100)


class PriceInOrder(models.Model):
    """Вспомогательная модель для сбора заказа из нескольких товаров."""
    price = models.ForeignKey(
        Price,
        verbose_name='Цена',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
    
    def __str__(self):
        return self.price.item.name