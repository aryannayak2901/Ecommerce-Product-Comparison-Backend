from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers.CustomUserSerializer import CustomUserSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from datetime import datetime, timedelta

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Mark inactive until OTP is verified
            otp = user.generate_otp()  # Generate OTP

            # Send OTP to user's email
            send_mail(
                'Your OTP Verification Code',
                f'Your OTP is: {otp}',
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'User registered successfully. Please verify OTP sent to your email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):

    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            
            if not user.is_active:
                return Response({"error": "Account is not verified. Please verify OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):

    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(email=email)

            # Check if OTP matches and is not expired
            if user.otp == otp and datetime.utcnow() <= user.otp_expiry:
                user.is_active = True  # Activate the user
                user.otp = None  # Clear OTP
                user.otp_expiry = None
                user.save()

                return Response({'message': 'OTP verified successfully. You can now log in.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ResendOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            user = CustomUser.objects.get(email=email)
            otp = user.generate_otp()

            # Resend OTP to user's email
            send_mail(
                'Your OTP Verification Code',
                f'Your OTP is: {otp}',
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'OTP has been resent to your email.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
