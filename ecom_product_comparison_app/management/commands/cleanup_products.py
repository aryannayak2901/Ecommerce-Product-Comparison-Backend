from django.core.management.base import BaseCommand
from ecom_product_comparison_app.tasks import cleanup_old_products

class Command(BaseCommand):
    help = 'Cleanup products older than 24 hours'

    def handle(self, *args, **options):
        cleanup_old_products()
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up old products')) 