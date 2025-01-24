from mongoengine import Document, StringField, BooleanField, DateTimeField
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
import random

class CustomUser(Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    full_name = StringField()
    is_active = BooleanField(default=False)  # Mark inactive until OTP is verified
    created_at = DateTimeField(default=datetime.utcnow)
    otp = StringField()  # Store OTP
    otp_expiry = DateTimeField()  # Store OTP expiry time

    def __str__(self):
        return self.email

    # Hash password
    def set_password(self, raw_password):
        self.password = pbkdf2_sha256.hash(raw_password)

    # Verify password
    def check_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    # Generate OTP
    def generate_otp(self):
        otp = str(random.randint(100000, 999999))  # 6-digit OTP
        self.otp = otp
        self.otp_expiry = datetime.utcnow() + timedelta(minutes=5)  # OTP valid for 5 minutes
        self.save()
        return otp
