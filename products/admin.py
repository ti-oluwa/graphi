from django.contrib import admin

from .models import Product, ProductCategory, ProductGroup

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductGroup)
