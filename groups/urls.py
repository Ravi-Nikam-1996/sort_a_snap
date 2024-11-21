from django.urls import path
from django.conf import settings
from .view.group_views import CustomGroupViewSet,JoinGroupView




urlpatterns = [
    path("get-customgroup-viewset/", CustomGroupViewSet.as_view({'get':'list'}), name="get_customgroup_viewset"),
    path("get-customgroup-viewset-create/", CustomGroupViewSet.as_view({'post':'create'}), name="customgroup_viewset_create"),
    path("get-customgroup-viewset-update/<int:pk>/", CustomGroupViewSet.as_view({'patch':'update'}), name="customgroup_viewset_update"),
    path("get-customgroup-viewset-delete/<int:pk>/", CustomGroupViewSet.as_view({'delete':'destroy'}), name="customgroup_viewset_delete"),
    path("get-customgroup-viewset-retrieve/<int:pk>/", CustomGroupViewSet.as_view({'get':'retrieve'}), name="customgroup_viewset_retrieve"),
    
    
    path("create-customgroupmember-viewset/", JoinGroupView.as_view({'post':'join'}), name="create_customgroupmember_viewset"),
    path("generate-OTP-viewset/", JoinGroupView.as_view({'post':'user_verify'}), name="generate_OTP_viewset"),
    path("confirm-OTP-viewset/", JoinGroupView.as_view({'post':'user_confirm'}), name="confirm_OTP_viewset"),
    
    
    
    
   
    # path("get-customgroupmember-viewset/", GroupMemberViewSet.as_view({'get':'list'}), name="get_customgroupmember_viewset"),
    # path("update-customgroupmember-viewset/<int:pk>/", GroupMemberViewSet.as_view({'patch':'update'}), name="update_customgroupmember_viewset"),
    # path("delete-customgroupmember-viewset/<int:pk>/", GroupMemberViewSet.as_view({'delete':'destroy'}), name="destroy_customgroupmember_viewset"),
    # path("retrieve-customgroupmember-viewset/<int:pk>/", GroupMemberViewSet.as_view({'get':'retrieve'}), name="retrieve_customgroupmember_viewset"),
    # path("generate-OTP-viewset/", GroupMemberViewSet.as_view({'post':'user_verify'}), name="generate_OTP_viewset"),
    # path("confirm-OTP-viewset/", GroupMemberViewSet.as_view({'post':'user_confirm'}), name="confirm_OTP_viewset"),
    
    
]
