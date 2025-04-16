from mongoengine import Document, StringField, BooleanField, DateTimeField, FloatField, URLField
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
import random

class CustomUser(Document):
    meta = {'collection': 'users'}
    
    # Add these class attributes for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    full_name = StringField()
    is_active = BooleanField(default=False)  # Mark inactive until OTP is verified
    is_staff = BooleanField(default=False)  # Add this for admin access
    is_superuser = BooleanField(default=False)  # Add this for superuser status
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

    # Add these methods for Django admin compatibility
    def get_username(self):
        return self.email

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    # Required for Django admin
    @property
    def pk(self):
        return str(self.id)

class Product(Document):
    meta = {'collection': 'products'}
    
    title = StringField(required=True)
    price = FloatField(required=True)
    source = StringField(required=True)
    link = StringField(required=True)
    image = URLField(required=True)
    rating = FloatField()
    search_query = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {'fields': ['created_at'], 'expireAfterSeconds': 86400}  # 24 hours
        ]
    }

    def __str__(self):
        return self.title

