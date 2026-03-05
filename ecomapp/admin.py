from django.contrib import admin

# Register your models here.
from .models import Product,Contact,Orders,OrderUpdate

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)

admin.site.site_header="SMARTCART admin"
admin.site.site_header="ECOMM admin portal"
admin.site.index_title="Welcome to SMARTCART ECOMMERCE Admin Portal"