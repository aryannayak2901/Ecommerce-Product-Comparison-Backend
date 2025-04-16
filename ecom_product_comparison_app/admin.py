from django.contrib import admin
from django_mongoengine import mongo_admin
from .models import CustomUser, Product

class CustomUserAdmin(mongo_admin.DocumentAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('created_at',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'is_staff', 'is_superuser'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

class ProductAdmin(mongo_admin.DocumentAdmin):
    list_display = ('title', 'price', 'source', 'created_at')
    search_fields = ('title', 'source')
    list_filter = ('source', 'created_at')
    ordering = ('-created_at',)

# Register with MongoEngine admin
mongo_admin.site.register(CustomUser, CustomUserAdmin)
mongo_admin.site.register(Product, ProductAdmin)
