from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError, PermissionDenied
from django.template.response import TemplateResponse

from .models import OrganizationProfile, OrganizationDocument, OrganizationVerificationEvent
from .services import VerificationService, DocumentService
from .exceptions import ConcurrencyConflictError


class OrganizationVerificationEventInline(admin.TabularInline):
    """Read-only inline showing complete verification audit event history."""
    model = OrganizationVerificationEvent
    extra = 0
    can_delete = False
    readonly_fields = ('event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')
    fields = ('event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrganizationDocumentInline(admin.TabularInline):
    """Inline displaying organization compliance documents with secure streaming links."""
    model = OrganizationDocument
    extra = 0
    can_delete = False
    readonly_fields = ('document_type', 'original_filename', 'review_status', 'secure_download_link', 'uploaded_at')
    fields = ('document_type', 'original_filename', 'review_status', 'secure_download_link', 'uploaded_at')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def secure_download_link(self, obj):
        if obj and obj.pk and obj.file:
            download_url = reverse('organization_document_download', kwargs={'doc_id': obj.id})
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer" style="font-weight: 600; color: #2563eb;">Download File</a>',
                download_url
            )
        return "-"
    secure_download_link.short_description = "Private Document"


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'org_type',
        'city',
        'verification_status',
        'created_at',
        'verified_by',
    )
    list_filter = ('verification_status', 'org_type', 'city', 'state')
    search_fields = (
        'name',
        'registration_number',
        'contact_person',
        'contact_email',
        'contact_phone',
        'city',
        'user__username',
        'user__email',
    )
    readonly_fields = (
        'id',
        'verified_by',
        'verified_at',
        'rejection_reason',
        'created_at',
        'updated_at',
    )
    inlines = [OrganizationDocumentInline, OrganizationVerificationEventInline]
    actions = ['approve_organization_action', 'reject_organization_action']

    fieldsets = (
        ('Organization Identity', {
            'fields': ('id', 'name', 'user', 'org_type', 'registration_number'),
        }),
        ('Authorized Contact', {
            'fields': ('contact_person', 'contact_email', 'contact_phone'),
        }),
        ('Physical Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'latitude', 'longitude'),
        }),
        ('Verification Governance', {
            'fields': ('verification_status', 'verified_by', 'verified_at', 'rejection_reason'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def approve_organization_action(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied("You do not have permission to modify organization profiles.")

        success_count = 0
        for org in queryset:
            try:
                VerificationService.approve_organization(request.user, org.id)
                success_count += 1
            except (ValidationError, ConcurrencyConflictError) as e:
                err_msg = e.messages if hasattr(e, 'messages') else [str(e)]
                self.message_user(
                    request,
                    f"Failed to approve '{org.name}': {'; '.join(err_msg)}",
                    level=messages.ERROR,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Unexpected error approving '{org.name}': {e}",
                    level=messages.ERROR,
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully approved {success_count} organization(s).",
                level=messages.SUCCESS,
            )

    approve_organization_action.short_description = "Approve selected organizations (Gate 2 Check)"

    def reject_organization_action(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied("You do not have permission to modify organization profiles.")

        if request.POST.get('post') == 'yes':
            rejection_reason = request.POST.get('rejection_reason', '').strip()
            if not rejection_reason:
                self.message_user(
                    request,
                    "Rejection reason is mandatory when rejecting organizations.",
                    level=messages.ERROR,
                )
                return None

            count = 0
            for org in queryset:
                try:
                    VerificationService.reject_organization(request.user, org.id, rejection_reason)
                    count += 1
                except (ValidationError, ConcurrencyConflictError) as e:
                    self.message_user(request, f"Error rejecting '{org.name}': {e}", level=messages.ERROR)
                except Exception as e:
                    self.message_user(request, f"Unexpected error rejecting '{org.name}': {e}", level=messages.ERROR)

            self.message_user(
                request,
                f"Successfully processed rejection for {count} organization(s).",
                level=messages.SUCCESS,
            )
            return None

        context = {
            'title': "Reject Selected Organizations",
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, 'admin/organizations/reject_organization_intermediate.html', context)

    reject_organization_action.short_description = "Reject selected organizations with mandatory reason"


@admin.register(OrganizationDocument)
class OrganizationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename',
        'organization',
        'document_type',
        'review_status',
        'secure_download_link',
        'uploaded_at',
    )
    list_filter = ('document_type', 'review_status', 'uploaded_at')
    search_fields = ('original_filename', 'organization__name', 'organization__registration_number')
    readonly_fields = (
        'id',
        'file_size_bytes',
        'content_type',
        'uploaded_at',
        'reviewed_by',
        'reviewed_at',
        'rejection_reason',
        'secure_download_link',
    )
    fields = (
        'organization',
        'document_type',
        'original_filename',
        'file_size_bytes',
        'content_type',
        'review_status',
        'reviewed_by',
        'reviewed_at',
        'rejection_reason',
        'secure_download_link',
        'uploaded_at',
    )
    actions = ['approve_document_action', 'reject_document_action']

    def secure_download_link(self, obj):
        if obj and obj.pk and obj.file:
            download_url = reverse('organization_document_download', kwargs={'doc_id': obj.id})
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer" style="font-weight: 600; color: #2563eb;">Download File</a>',
                download_url
            )
        return "-"
    secure_download_link.short_description = "Private Document"

    def approve_document_action(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied("You do not have permission to modify organization documents.")

        count = 0
        for doc in queryset:
            try:
                DocumentService.review_document(request.user, doc.id, OrganizationDocument.ReviewStatus.APPROVED)
                count += 1
            except Exception as e:
                self.message_user(request, f"Error approving '{doc.original_filename}': {e}", level=messages.ERROR)

        if count > 0:
            self.message_user(request, f"Approved {count} document(s).", level=messages.SUCCESS)

    approve_document_action.short_description = "Approve selected documents"

    def reject_document_action(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied("You do not have permission to modify organization documents.")

        if request.POST.get('post') == 'yes':
            rejection_reason = request.POST.get('rejection_reason', '').strip()
            if not rejection_reason:
                self.message_user(request, "Rejection reason is mandatory when rejecting documents.", level=messages.ERROR)
                return None

            count = 0
            for doc in queryset:
                try:
                    DocumentService.review_document(request.user, doc.id, OrganizationDocument.ReviewStatus.REJECTED, rejection_reason)
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Error rejecting '{doc.original_filename}': {e}", level=messages.ERROR)

            self.message_user(request, f"Rejected {count} document(s).", level=messages.SUCCESS)
            return None

        context = {
            'title': "Reject Selected Documents",
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, 'admin/organizations/reject_document_intermediate.html', context)

    reject_document_action.short_description = "Reject selected documents with mandatory reason"


@admin.register(OrganizationVerificationEvent)
class OrganizationVerificationEventAdmin(admin.ModelAdmin):
    list_display = ('organization', 'event_type', 'actor', 'previous_status', 'new_status', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('organization__name', 'actor__username', 'notes')
    readonly_fields = ('id', 'organization', 'event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
