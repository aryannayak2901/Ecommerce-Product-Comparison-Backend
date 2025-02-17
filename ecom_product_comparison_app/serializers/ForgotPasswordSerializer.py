from rest_framework import serializers
from ..models import CustomUser
from datetime import datetime
import random

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")
        
        # Generate OTP and set expiry
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        user.save()

        # Send OTP via email (You need to implement the actual email sending)
        send_reset_email(user.email, otp)  # Implement this function separately

        return value
