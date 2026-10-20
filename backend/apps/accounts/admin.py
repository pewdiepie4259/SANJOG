from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model with defense-in-depth role and privilege guards."""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'username',
        'email',
        'role',
        'is_email_verified',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    list_filter = (
        'role',
        'is_email_verified',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('id', 'date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('SANJOG Governance', {'fields': ('role', 'is_email_verified')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'role',
                'phone_number',
                'first_name',
                'last_name',
                'usable_password',
                'password1',
                'password2',
            ),
        }),
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        BaseFormClass = super().get_form(request, obj, change=change, **kwargs)

        class RequestBoundCustomUserForm(BaseFormClass):
            def __init__(self, *args, **form_kwargs):
                form_kwargs['current_user'] = request.user
                super().__init__(*args, **form_kwargs)

        return RequestBoundCustomUserForm

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            for f in ['is_superuser', 'is_staff', 'groups', 'user_permissions']:
                if f not in ro:
                    ro.append(f)
            if obj and obj.role == CustomUser.RoleChoices.ADMIN:
                if 'role' not in ro:
                    ro.append('role')
        return ro

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser:
            return (
                (None, {'fields': ('id', 'username')}),
                ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
                ('SANJOG Governance', {'fields': ('role', 'is_email_verified')}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        return super().get_fieldsets(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            if obj.is_superuser:
                return False
            if obj.role == CustomUser.RoleChoices.ADMIN:
                return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            if obj.is_superuser:
                return False
            if obj.role == CustomUser.RoleChoices.ADMIN:
                return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            if not change:
                if obj.role == CustomUser.RoleChoices.ADMIN:
                    raise PermissionDenied("Only superusers can create accounts with the Platform Administrator role.")
                obj.is_superuser = False
            else:
                original = CustomUser.objects.get(pk=obj.pk)
                if original.role != CustomUser.RoleChoices.ADMIN and obj.role == CustomUser.RoleChoices.ADMIN:
                    raise PermissionDenied("Only superusers can assign the Platform Administrator role.")
                if original.role == CustomUser.RoleChoices.ADMIN:
                    obj.role = original.role
                obj.is_superuser = original.is_superuser
                obj.is_staff = original.is_staff
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        if not request.user.is_superuser and change:
            orig_user = CustomUser.objects.get(pk=form.instance.pk)
            orig_groups = list(orig_user.groups.all())
            orig_perms = list(orig_user.user_permissions.all())
            super().save_related(request, form, formsets, change)
            form.instance.groups.set(orig_groups)
            form.instance.user_permissions.set(orig_perms)
        else:
            super().save_related(request, form, formsets, change)


