from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from imagesense.serializers import UserProfileSerializer

from rest_framework import serializers
from groups.model.group import CustomGroup, GroupMember
User = get_user_model()

class GroupMemberSerializer(serializers.ModelSerializer):
    # import ipdb;ipdb.set_trace()
    user = UserProfileSerializer()  # Assuming this is a nested serializer for user data

    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'user', 'role', 'joined_at', 'user_verified']
        read_only_fields = ['joined_at']
    
    
    def validate_group(self, value):
        # Check if group exists
        if not CustomGroup.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Group does not exist.")
        return value
    
    
    def create(self, validated_data):
        # Get the user by email
        import ipdb;ipdb.set_trace()  

        user_email = validated_data.pop('user')
        try:
            user = get_user_model().objects.get(email=user_email)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError({"user": "User with this email does not exist."})

        # Create the GroupMember instance
        group_member = GroupMember.objects.create(user=user, **validated_data)
        return group_member
    
    
    # def create(self, validated_data):
    #     # Automatically assign the authenticated user (if user is authenticated)
    #     validated_data['user'] = self.context['request'].user
    #     return super().create(validated_data)
    
    
    
    
    
    
    
    
    
    # def validate_user(self, value):
    #     if not isinstance(value, dict):
    #         raise serializers.ValidationError("The 'user' field must be a dictionary.")
    #     return value

    # def create(self, validated_data):
    #     # Extract nested user data``````````````````````````````````````````````````````
    #     # import ipdb;ipdb.set_trace()  
    #     user_data = validated_data.pop('user')
    #     # mobile_number = validated_data.get('phone_no')  
    #     # Create or update the user
    #     # print("=================>>>>>>>>>>.",mobile_number,user_data)
    #     user, created = User.objects.get_or_create(
    #         phone_no=user_data.get('phone_no'),
    #         defaults={
    #             "email": user_data.get("email", ""),
    #             "first_name": user_data.get("first_name", ""),
    #             "last_name": user_data.get("last_name", ""),
    #             "phone_no": user_data.get("phone_no", ""),
    #             "otp_status":True
    #         }
    #     )
    #     if not created:
    #         for key, value in user_data.items():
    #             setattr(user, key, value)
    #         user.save()
    #     validated_data["user_verified"] = True
    #     validated_data["user"] = user

    #     group_member = GroupMember.objects.create(**validated_data)
    #     return group_member
    
    # def update(self, instance, validated_data):
        # import ipdb;ipdb.set_trace()
        user_data = validated_data.pop('user',{})
        user_data.pop('email', None)
        new_email = user_data.get('email', None)
        phone_no = user_data.get('phone_no', None)

      
        if new_email and new_email != instance.email:
            if User.objects.exclude(pk=instance.pk).filter(email=new_email).exists():
                raise serializers.ValidationError("Email address must be unique.")
            
        if new_email and instance.user.email and instance.user.email != new_email:
            raise serializers.ValidationError({"email": "Email cannot be updated once it's set."})

        
        if phone_no and instance.user.phone_no and instance.user.phone_no != phone_no:
            raise serializers.ValidationError({"phone_no": "Phone number cannot be updated once it's set."})

        
        for attr, value in user_data.items():
            # if attr not in ['email', 'phone_no']: 
            setattr(instance.user, attr, value)
        
        instance.user.save()
        
        instance.role = validated_data.get('role', instance.role)
        instance.group = validated_data.get('group', instance.group)
        instance.save()

        return instance
    
    # def to_representation(self, instance):
    #     request = self.context.get('request')
    #     from_method = self.context.get('from_method', 'unknown')

    #     def get_common_fields(instance):
    #         return {
    #             "role": instance.role,
    #             "joined_at": instance.joined_at,
    #         }

    #     common_fields = get_common_fields(instance)

    #     if request and request.method == 'GET' and 'pk'  in request.resolver_match.kwargs:
    #         # If specific group member details are requested
    #         member_data = {
    #             "id": instance.id,
    #             "group": instance.group.id,
    #             "user": instance.user.id,
    #             "role": instance.role,
    #             "joined_at": instance.joined_at,
    #             **common_fields,
    #         }
    #         return member_data

    #     elif from_method == 'list':
    #         # If listing all members with a simplified structure
    #         member_data = {
    #             "user": instance.user.id,
    #             "role": instance.role,
    #             "group_id": instance.group.id if instance.group else None,
    #             "group_name": instance.group.name if instance.group else None,
    #             **common_fields,
    #         }
    #         return member_data
        
    #     elif from_method == 'updates':
    #         member_data = {
    #             "user": instance.user.id,
    #             "first_name": instance.user.first_name,
    #             "last_name" : instance.user.last_name,
    #             # "role": instance.role,
    #             "group_id": instance.group.id if instance.group else None,
    #             "group_name": instance.group.name if instance.group else None,
    #              **common_fields,
    #         }
    #         return member_data
    #     else:
    #         # Default case: Provide basic member details
    #         member_data = {
    #             "id": instance.id,
    #             "group": instance.group.id,
    #             "user": instance.user.id,
    #             "role": instance.role,
    #             "joined_at": instance.joined_at,
    #             **common_fields,
    #         }
    #         return member_data


class CustomGroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(source='groupmember_set', many=True, read_only=True)

    class Meta:
        model = CustomGroup
        fields = ['id', 'name', 'access', 'thumbnail', 'members','code']
        read_only_fields = ['code'] 
        
    def to_representation(self, instance):
        request = self.context.get('request')
        from_method = self.context.get('from_method', 'unknown')

        def get_common_fields(instance):
            """Helper function to extract common fields for all conditions."""
            return {
                "name": instance.name,
                "access": instance.access,
                "thumbnail": instance.thumbnail.url if instance.thumbnail else None
            }

        common_fields = get_common_fields(instance)

        if request and request.method == 'GET':
            # If specific group details are requested
            group_data = {
                "id": instance.id,
                "name": instance.name,
                "access": instance.access,
                "code": instance.code,
                "thumbnail": instance.thumbnail.url if instance.thumbnail else None,
                "members": self.context.get('members', []),  # Include members if available
                **common_fields,
            }
            return group_data

        elif from_method == 'list_groups':
            # If listing all groups with a simplified structure
            group_data = {
                "name": instance.name,
                "access": instance.access,
                **common_fields,
            }
            return group_data

        else:
            # Default case: Provide basic group details
            group_data = {
                "id": instance.id,
                "name": instance.name,
                "access": instance.access,
                "code": instance.code,
                "thumbnail": instance.thumbnail.url if instance.thumbnail else None,
                **common_fields,
            }
            return group_data