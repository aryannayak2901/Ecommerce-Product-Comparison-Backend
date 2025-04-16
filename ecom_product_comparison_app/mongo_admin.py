from django.contrib import admin
from mongoengine.base import BaseDocument
from django_mongoengine import mongo_admin

class MongoModelAdmin(admin.ModelAdmin):
    """Base class for administrating MongoEngine documents"""
    
    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__(model, admin_site)

    def get_queryset(self, request):
        """Use MongoEngine's objects manager"""
        return self.model.objects

    def save_model(self, request, obj, form, change):
        """Save MongoEngine document"""
        obj.save()

    def delete_model(self, request, obj):
        """Delete MongoEngine document"""
        obj.delete()

    def get_object(self, request, object_id):
        """Get object by primary key"""
        try:
            return self.model.objects.get(id=object_id)
        except self.model.DoesNotExist:
            return None 

class DocumentAdmin(mongo_admin.DocumentAdmin):
    """Base admin class for MongoEngine documents"""
    pass 