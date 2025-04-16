from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers.CustomUserSerializer import CustomUserSerializer
from .serializers.ForgotPasswordSerializer import ForgotPasswordSerializer
from .models import CustomUser, Product
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.core.cache import cache  # Use cache to store verified users temporarily
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .scraper_service import ScraperService



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
            print("abc login")
            if not user.is_active:
                print("verified")
                return Response({"error": "Account is not verified. Please verify OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                print(refresh.access_token, refresh)
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

                refresh = RefreshToken.for_user(user)
                print(refresh.access_token, refresh)

                return Response({'message': 'OTP verified successfully. You can now log in.', 'access_token': str(refresh.access_token), 'refresh_token': str(refresh),}, status=status.HTTP_200_OK)
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


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Password reset OTP sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not new_password or not confirm_password:
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email was verified via OTP
        verified_email = cache.get(f'verified_{email}')
        if not verified_email:
            return Response({"message": "OTP verification required."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.get(email=email)
            user.password = make_password(new_password)  # Hash the new password
            user.save()
            cache.delete(f'verified_{email}')  # Remove the verification flag after successful reset
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        




class ProductSearchView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            query = request.query_params.get('query', '').strip()
            
            if not query:
                return Response({"error": "Query parameter is required"}, status=400)

            # Get cached results if they exist
            cache_key = f'search_results_{query}'
            cached_results = cache.get(cache_key)
            
            if cached_results:
                # Check if products are still valid
                product_ids = [p.get('id') for p in cached_results]
                valid_products = Product.objects(id__in=product_ids, 
                                              created_at__gte=datetime.utcnow() - timedelta(hours=24))
                
                if valid_products.count() == len(cached_results):
                    return Response({
                        "query": query,
                        "total_products": len(cached_results),
                        "products": cached_results
                    })
                else:
                    # If some products expired, clear cache
                    cache.delete(cache_key)

            # If no cached results or cache invalid, scrape new data
            scraper_service = ScraperService()
            products = scraper_service.scrape_products(query)

            if not products:
                return Response({
                    "query": query,
                    "total_products": 0,
                    "products": []
                })

            # Format and save products
            formatted_products = []
            for product in products:
                try:
                    formatted_product = {
                        'title': product['name'],
                        'price': float(product['price'].replace(',', '')),
                        'source': product['source'],
                        'link': product['url'],
                        'image': product['image'],
                        'rating': float(product['rating']) if product.get('rating') else 0
                    }
                    
                    # Save to database with timestamp
                    saved_product = Product(
                        **formatted_product,
                        search_query=query,
                        created_at=datetime.utcnow()
                    ).save()
                    
                    formatted_product['id'] = str(saved_product.id)
                    formatted_products.append(formatted_product)
                except Exception as e:
                    print(f"Error formatting product: {str(e)}")
                    continue

            # Cache results for 1 hour
            cache.set(cache_key, formatted_products, 3600)

            return Response({
                "query": query,
                "total_products": len(formatted_products),
                "products": formatted_products
            })

        except Exception as e:
            print(f"Search error: {str(e)}")
            return Response({
                "error": "An error occurred while processing your request",
                "query": query,
                "total_products": 0,
                "products": []
            }, status=500)

