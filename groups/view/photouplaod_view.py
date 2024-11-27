from rest_framework import viewsets
from groups.model.group import photo_group
from groups.serializers.group_serializers import photo_serializer
from rest_framework.permissions import IsAuthenticated  
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from face.function_call import StandardResultsSetPagination,Global_error_message,check_required_fields
import boto3
from django.http import Http404


User = get_user_model()

rekognition_client = boto3.client('rekognition', region_name='us-west-2')  # Update the region as needed


def detect_faces(image_data):
    try:
        # Use AWS Rekognition to detect faces in the image
        response = rekognition_client.detect_faces(
            Image={'Bytes': image_data},  # Send image as bytes
            Attributes=['ALL']  # Optionally specify what you need (e.g., 'DEFAULT', 'ALL')
        )
        # Extract face details from the response
        return response.get('FaceDetails', [])
    except Exception as e:
        print(f"Error in Rekognition: {e}")
        return []


class PhotoGroupViewSet(viewsets.ModelViewSet):
    queryset = photo_group.objects.all()
    serializer_class = photo_serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    filterset_fields = ['photo_name']
    search_fields = ['photo_name']
    
    def get_queryset(self):
        return super().get_queryset()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            if not queryset.exists():
                return Response({
                    "status": False,
                    "message": "No groups found!",
                    'data': []
                }, status=status.HTTP_204_NO_CONTENT)
                
            serializer = self.serializer_class(queryset, many=True)
            return Response({
                "status": True,
                "message": "Groups retrieved successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': "Something went wrong!",
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def get_list(self, request, *args, **kwargs):
        user = request.data.get('user')
        if not user:
            return Response(
                {"status":False,'message': 'user_id is required in the request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = get_user_model().objects.get(id=user) 
            photos = photo_group.objects.filter(user=user)
            serializer = self.get_serializer(photos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except user.DoesNotExist:
            return Response(
                {"status":False,'message': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

            
    def get_group_wise_user(self, request, *args, **kwargs):
        user = request.data.get('user')
        group = request.data.get('group')
        if not user:
            return Response(
                {"status":False,'message': 'user_id is required '},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not group:
            return Response(
                {"status":False,'message': 'group is required '},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            photos = photo_group.objects.filter(user_id=user, group__id=group) if group else photo_group.objects.filter(user_id=user)
            if not photos.exists():
                return Response(
                    {"status":False,'message': 'No photos found for the given user and group'},
                status=status.HTTP_404_NOT_FOUND
            )
            serializer = self.get_serializer(photos, many=True)
            return Response({ "status": True,  
                             "message": "group and user wise Data retrieved successfully.",
                             "data":serializer.data}, status=status.HTTP_200_OK)
        
        except user.DoesNotExist:
            return Response(
                {"status": False,'message': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
              
    def create(self, request, *args, **kwargs):
        try:
            required_fields = ["photo_name","image","user","group"]
            error_message = check_required_fields(required_fields, request.data)
            if error_message:
                return Response({"status": False, "message": error_message},status=status.HTTP_400_BAD_REQUEST)
            # import ipdb;ipdb.set_trace()
            image_file = request.FILES['image']
            if not image_file:
                return Response({"status": False, "message": "Uploaded 'image' file is invalid"},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                image_data = image_file.read()
            except Exception as e:
                return Response({"status": False, "message": f"Error reading 'image': {str(e)}"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.serializer_class(data=request.data,context={'request': request})
            if serializer.is_valid():   
                photo_group = serializer.save() 
                # face_details = detect_faces(image_data)
                # photo_group.face_details = str(face_details) 
                photo_group.save()
                return Response({'status': True, 'message': 'Upload photo successfully'},status=status.HTTP_201_CREATED)
            else:
                return Response({'status': False, 'message': 'Failed to upload photo', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':False,
                    'message':Global_error_message,
                    'error':str(e)}, status.HTTP_400_BAD_REQUEST)
    
    
    def update(self, request, *args, **kwargs):
        try:
            photo_group_id = kwargs.get('pk')  
            photo_group = self.get_object()  

            required_fields = ["photo_name", "image", "user", "group"]
            error_message = check_required_fields(required_fields, request.data)
            if error_message:
                return Response({"status": False, "message": error_message}, status=status.HTTP_400_BAD_REQUEST)

            image_file = request.FILES.get('image', None)
            if image_file:
                try:
                    image_data = image_file.read()
                except Exception as e:
                    return Response({"status": False, "message": f"Error reading 'image': {str(e)}"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                if not image_file:
                    return Response({"status": False, "message": "Uploaded 'image' file is invalid"},
                                    status=status.HTTP_400_BAD_REQUEST)
                photo_group.image = image_file

            # Update other fields
            photo_group.photo_name = request.data.get('photo_name', photo_group.photo_name)
            photo_group.user_id = request.data.get('user', photo_group.user)
            photo_group.group_id = request.data.get('group', photo_group.group)

            # Save the updated object
            photo_group.save()

            return Response({'status': True, 'message': 'Photo group updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': False,
                            'message': Global_error_message,
                            'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print("instance",instance)
            if instance:
                instance.delete()
            return Response({'status': True, 'message': 'photo deleted successfully'}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'status': False, 'message': "User not found!"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':False,
                    'message':"Something went wrong !!",
                    'error':str(e)},status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.serializer_class(instance, context={'request': request})
            return Response({'status': True, 'message': 'photo data retrieved successfully.', 'data': {"user":serializer.data}} ,status=status.HTTP_200_OK)
        except Http404:
            return Response({'status': False, 'message': 'Data not found.'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False, 'message': "something went wrong ! ", 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)