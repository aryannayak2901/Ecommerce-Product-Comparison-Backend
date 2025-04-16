from django.apps import AppConfig


class EcomProductComparisonAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecom_product_comparison_app'

    def ready(self):
        # Import and register signals if needed
        pass
