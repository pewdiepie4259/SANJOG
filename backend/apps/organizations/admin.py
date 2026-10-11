from django.contrib import admin
from .models import OrganizationProfile, OrganizationDocument, OrganizationVerificationEvent

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'org_type', 'city', 'verification_status', 'created_at')
    list_filter = ('verification_status', 'org_type', 'city')
    search_fields = ('name', 'registration_number', 'user__username', 'contact_person', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(OrganizationDocument)
class OrganizationDocumentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'organization', 'document_type', 'review_status', 'uploaded_at')
    list_filter = ('document_type', 'review_status')
    search_fields = ('original_filename', 'organization__name')
    readonly_fields = ('id', 'uploaded_at', 'file_size_bytes', 'content_type')


@admin.register(OrganizationVerificationEvent)
class OrganizationVerificationEventAdmin(admin.ModelAdmin):
    list_display = ('organization', 'event_type', 'actor', 'previous_status', 'new_status', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('organization__name', 'actor__username', 'notes')
    readonly_fields = ('id', 'organization', 'event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
