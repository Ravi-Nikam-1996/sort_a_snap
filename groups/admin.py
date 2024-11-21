# from django.contrib import admin
# from django.contrib.auth.models import Group as AuthGroup
from django.contrib import admin
from django.contrib.auth.models import User
from groups.model.group import CustomGroup, GroupMember

# Inline model for managing group members within the CustomGroup admin page
class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1  # Number of empty forms to display
    fk_name = 'group'
    fields = ['user', 'role', 'joined_at']
    readonly_fields = ['joined_at']
    can_delete = False

# Custom Group admin to manage CustomGroup with additional fields
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'access', 'thumbnail', 'created_by']
    search_fields = ['id','name', 'access']
    list_filter = ['access']
    inlines = [GroupMemberInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['id','group', 'user', 'role', 'joined_at']
    search_fields = ['id','group__name', 'user__username', 'role']
    list_filter = ['id','role']
    readonly_fields = ['id','joined_at']

# Register models in admin
admin.site.register(CustomGroup, CustomGroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)