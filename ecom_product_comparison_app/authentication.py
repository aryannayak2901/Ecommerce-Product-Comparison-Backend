from rest_framework_simplejwt.authentication import JWTAuthentication
from ecom_product_comparison_app.models import CustomUser
from mongoengine.queryset.visitor import Q

class MongoDBJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            user = CustomUser.objects.get(Q(email=user_id))  # Fetch user by email
            return user
        except CustomUser.DoesNotExist:
            return None
