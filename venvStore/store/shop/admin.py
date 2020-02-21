from django.contrib import admin
from . import models
from mptt.admin import MPTTModelAdmin


class CategoryMPTTModelAdmin(MPTTModelAdmin):
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20


class CartItemAdmin(admin.ModelAdmin):
    """Товары в корзине"""
    list_display = ('cart', 'product', 'quantity')

class ProductAdmin(admin.ModelAdmin):
    """Продукты"""
    list_display = ("title", "category", "price", "quantity")
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(models.Category, CategoryMPTTModelAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Cart)
admin.site.register(models.CartItem, CartItemAdmin)
admin.site.register(models.Order)
