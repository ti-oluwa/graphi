from django.contrib import admin

from .models import Product, ProductGroup, ProductBrand

admin.site.register(Product)
admin.site.register(ProductGroup)
admin.site.register(ProductBrand)
