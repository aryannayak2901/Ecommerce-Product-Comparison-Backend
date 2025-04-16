from datetime import datetime, timedelta
from .models import Product

def cleanup_old_products():
    """
    Remove products older than 24 hours
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    Product.objects(created_at__lte=cutoff_time).delete() 