# Create your views here.
# my_app/views.py
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import send_otp
from .serializers import OTPSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django.http import Http404
from face.exceptions import CustomError
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import BlackListedToken 


User = get_user_model()

class GenerateOTP(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if user.otp_status:
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    return Response({
                        "message": "User already exists !!",
                        "token": access_token
                    }, status=status.HTTP_200_OK)
                else:
                    send_otp.delay(email)
                    return Response({"message": f"OTP sent successfully to {email}"}, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                send_otp.delay(email) 
                return Response({"message": f"OTP sent successfully to {email}"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        cached_otp = cache.get(f"otp_{email}")

        if cached_otp == int(otp):
            user, _ = User.objects.get_or_create(email=email)
            user.otp_status_email = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({'status':True,'message':'Login successfully !!',
                'data':{'refresh': str(refresh),'access': str(refresh.access_token),'email':user.email,'otp_status':user.otp_status}
            }, status=status.HTTP_200_OK)
        
        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def logout(self, request, *args, **kwargs):
        try:
            import ipdb;ipdb.set_trace()
            access_token = request.headers.get('Authorization')
            if access_token is None or not access_token.startswith('Bearer '):
                return Response({
                    'status': False,
                    'message': 'Access token is missing or invalid'
                }, status=status.HTTP_400_BAD_REQUEST)

            access_token = access_token.split(' ')[1]  
            try:
                token = AccessToken(access_token)
                cache.set(f'blacklisted_{access_token}', True, timeout=token.lifetime.total_seconds())
                user = request.user 
                BlackListedToken.objects.create(token=access_token, user=user)
                
                return Response({
                    'status': True,
                    'message': 'User logged out successfully'
                }, status=status.HTTP_200_OK)
            except TokenError:
                return Response({
                    'status': False,
                    'message': 'Token is invalid or expired'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset()

    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            if not instance.is_active:
                raise CustomError("User is inactive", code="user_inactive")

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'status': True, 'message': 'User updated successfully', 'data': {'user':serializer.data}}, status=status.HTTP_200_OK)
        except CustomError as e:
             return Response({
            'status': False,
            'message': e.message,
            'code': e.code
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
            
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print("instance",instance)
            if instance:
                instance.delete()
            return Response({'status': True, 'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'status': False, 'message': "User not found!"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':False,
                    'message':"Something went wrong !!",
                    'error':str(e)},status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        # import ipdb;ipdb.set_trace()
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance, context={'request': request})
            return Response({'status': True, 'message': 'User data retrieved successfully.', 'data': {"user":serializer.data}} ,status=status.HTTP_200_OK)
        except Http404:
            return Response({'status': False, 'message': 'Data not found.'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False, 'message': "something went wrong ! ", 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    def verified_user_retrived(self, request, *args, **kwargs):
        try:
            phone_numbers = request.data.get("phone_no", [])
            
            if not phone_numbers or not isinstance(phone_numbers, list):
                return Response({
                    "status": False,
                    "message": "Invalid or missing phone_numbers list.",
                    "data": []
                }, status=status.HTTP_400_BAD_REQUEST)

            users = User.objects.filter(phone_no__in=phone_numbers, otp_status=True)
            
            if not users.exists():
                return Response({
                    "status": False,
                    "message": "No users found with otp_status True.",
                    "data": []
                }, status=status.HTTP_204_NO_CONTENT)
            
            serializer = UserProfileSerializer(users, many=True, context={"request": request})
            return Response({
                "status": True,
                "message": "Users with otp_status True.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status": False,
                "message": "Something went wrong!",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST) 
        
# class GenerateOTP(APIView):
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             print("--->",email)
#             res=send_otp.delay(email)  # Call the task asynchronously
#             print("===>>",res)
#             return Response({"message": f"OTP sent successfully to {email}"},status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def create(self, request, *args, **kwargs):
    #     try:update
    #         email = request.data.get('email')
    #         # if CustomUser.objects.filter(email=email).exists():
    #         #     return Response({'status': False, 'message': 'Email already exists'},
    #         #                 status=status.HTTP_400_BAD_REQUEST)
    #         # username = request.data.get('username')
    #         # if CustomUser.objects.filter(username=username).exists():
    #         #     return Response({'status': False, 'message': 'username already exists'},
    #         #                 status=status.HTTP_400_BAD_REQUEST)
                
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_create(serializer)
    #         return Response({'status': True, 'message': 'User created successfully'},
    #                         status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         return Response({'status': False, 'message': 'Failed to create User', 'error': str(e)},
    #                         status=status.HTTP_400_BAD_REQUEST)
    
    
    
    # def update(self, request, *args, **kwargs):
    #     try:
    #         partial = kwargs.pop('partial', True)
    #         instance = self.get_object()
    #         serializer = self.serializer_class(instance, data=request.data, partial=partial,context={'request': request})
            
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({'status': True, 'message': 'User updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            
    #         error_message = "wrong"
    #         return Response({'status': False, 'message': 'Failed to update User', 'errors': error_message}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({'status':False,
    #                 'message':"Might be some error !! ",
    #                 'error':str(e)},status=status.HTTP_400_BAD_REQUEST)


# class EditProfile(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request):
#         user = request.user  # Access the authenticated user
#         serializer = UserProfileSerializer(user, data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Profile updated successfully"}, status=200)
        
#         return Response(serializer.errors, status=400)
