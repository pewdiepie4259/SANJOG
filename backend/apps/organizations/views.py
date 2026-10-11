from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from apps.accounts.decorators import role_required, admin_required
from .models import OrganizationProfile, OrganizationDocument
from .forms import (
    OrganizationProfileForm,
    OrganizationDocumentUploadForm,
    AdminOrganizationRejectForm,
    AdminDocumentReviewForm
)
from .services import OrganizationService, DocumentService, VerificationService
from .validators import REQUIRED_DOCUMENTS_BY_ORG_TYPE
from .exceptions import ConcurrencyConflictError


@login_required(login_url='/login/')
def onboarding_view(request):
    """Introductory onboarding screen for Donors and Receivers."""
    if request.user.is_volunteer:
        messages.warning(request, "Rescue Volunteers operate as individual agents and do not require organization onboarding.")
        return redirect('/volunteer/dashboard/')

    if hasattr(request.user, 'organization_profile'):
        return redirect('organization_profile')

    return render(request, 'organizations/onboarding.html', {
        'role_display': request.user.get_role_display()
    })


class OrganizationCreateView(View):
    """HTML / HTMX View for creating an organization profile."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        if request.user.is_volunteer:
            return render(request, '403.html', {'error_message': 'Volunteers cannot create organization profiles.'}, status=403)

        if hasattr(request.user, 'organization_profile'):
            return redirect('organization_profile')

        form = OrganizationProfileForm(user=request.user)
        return render(request, 'organizations/profile_form.html', {'form': form, 'is_create': True})

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request):
        if request.user.is_volunteer:
            return render(request, '403.html', {'error_message': 'Volunteers cannot create organization profiles.'}, status=403)

        form = OrganizationProfileForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                org = OrganizationService.create_profile(
                    user=request.user,
                    **form.cleaned_data
                )
                messages.success(request, f"Organization profile '{org.name}' created! Please upload your verification documents.")
                redirect_url = '/organizations/documents/'
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=200)
                    response['HX-Redirect'] = redirect_url
                    return response
                return redirect(redirect_url)
            except DjangoValidationError as e:
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field if field in form.fields else None, err)

        if request.headers.get('HX-Request'):
            return render(request, 'organizations/profile_form.html', {'form': form, 'is_create': True}, status=400)
        return render(request, 'organizations/profile_form.html', {'form': form, 'is_create': True})


class OrganizationProfileDetailView(View):
    """Overview of organization profile, documents status, and audit history."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])
        uploaded_types = set(org.documents.values_list('document_type', flat=True))

        checklist = []
        for req in required_types:
            docs = org.documents.filter(document_type=req)
            has_approved = docs.filter(review_status=OrganizationDocument.ReviewStatus.APPROVED).exists()
            has_pending = docs.filter(review_status=OrganizationDocument.ReviewStatus.PENDING).exists()
            has_rejected = docs.filter(review_status=OrganizationDocument.ReviewStatus.REJECTED).exists()
            
            status_text = 'MISSING'
            if has_approved:
                status_text = 'APPROVED'
            elif has_pending:
                status_text = 'PENDING'
            elif has_rejected:
                status_text = 'REJECTED'

            checklist.append({
                'type': req,
                'label': req.label,
                'status': status_text,
                'is_satisfied': (has_approved or has_pending)
            })

        return render(request, 'organizations/profile_detail.html', {
            'organization': org,
            'checklist': checklist,
            'documents': org.documents.all(),
            'events': org.verification_events.all()[:10],
        })


class OrganizationProfileEditView(View):
    """Edit draft or rejected organization profile."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        if org.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            messages.warning(request, "Organization profile is locked while pending administrative review.")
            return redirect('organization_profile')

        form = OrganizationProfileForm(instance=org, user=request.user)
        return render(request, 'organizations/profile_form.html', {'form': form, 'organization': org, 'is_create': False})

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        form = OrganizationProfileForm(request.POST, instance=org, user=request.user)
        if form.is_valid():
            try:
                OrganizationService.update_profile(request.user, org.id, **form.cleaned_data)
                messages.success(request, "Organization profile details updated successfully.")
                redirect_url = '/organizations/profile/'
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=200)
                    response['HX-Redirect'] = redirect_url
                    return response
                return redirect(redirect_url)
            except DjangoValidationError as e:
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field if field in form.fields else None, err)

        if request.headers.get('HX-Request'):
            return render(request, 'organizations/profile_form.html', {'form': form, 'organization': org, 'is_create': False}, status=400)
        return render(request, 'organizations/profile_form.html', {'form': form, 'organization': org, 'is_create': False})


class OrganizationSubmitView(View):
    """Submit organization for verification."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        try:
            OrganizationService.submit_for_verification(request.user, org.id)
            messages.success(request, "Organization profile submitted for administrative verification! Our team will review your credentials.")
        except DjangoValidationError as e:
            msg = e.message_dict.get('documents', [str(e)])[0] if hasattr(e, 'message_dict') else str(e)
            messages.error(request, msg)
        except Exception as e:
            messages.error(request, str(e))

        return redirect('organization_profile')


class OrganizationDocumentManageView(View):
    """View and upload verification documents."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        form = OrganizationDocumentUploadForm()
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])
        
        return render(request, 'organizations/document_manage.html', {
            'organization': org,
            'form': form,
            'documents': org.documents.all(),
            'required_types': required_types,
        })


class OrganizationDocumentUploadView(View):
    """Process verification document upload."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return redirect('organization_onboarding')

        org = request.user.organization_profile
        form = OrganizationDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                doc = DocumentService.upload_document(
                    user=request.user,
                    org_id=org.id,
                    document_type=form.cleaned_data['document_type'],
                    uploaded_file=form.cleaned_data['file']
                )
                messages.success(request, f"Document '{doc.original_filename}' uploaded successfully.")
                return redirect('organization_documents')
            except DjangoValidationError as e:
                for field, errs in e.message_dict.items():
                    for err in errs:
                        messages.error(request, err)
            except Exception as e:
                messages.error(request, str(e))
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field.capitalize()}: {err}")

        return redirect('organization_documents')


class OrganizationDocumentDownloadView(View):
    """Securely stream private document with verification."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request, doc_id):
        doc = get_object_or_404(OrganizationDocument, id=doc_id)
        if doc.organization.user != request.user and not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'You do not have permission to download this document.'}, status=403)

        try:
            file_handle = doc.file.open('rb')
            response = FileResponse(file_handle, content_type=doc.content_type)
            response['Content-Disposition'] = f'attachment; filename="{doc.original_filename}"'
            response['X-Content-Type-Options'] = 'nosniff'
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            response['Content-Security-Policy'] = "default-src 'none'"
            return response
        except FileNotFoundError:
            raise Http404("Document file does not exist on storage.")


class OrganizationDocumentDeleteView(View):
    """Delete draft/rejected document."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request, doc_id):
        doc = get_object_or_404(OrganizationDocument, id=doc_id)
        try:
            DocumentService.delete_document(request.user, doc.id)
            messages.info(request, f"Document '{doc.original_filename}' deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect('organization_documents')


# ==========================================
# ADMIN VERIFICATION QUEUE & REVIEW VIEWS
# ==========================================

class AdminVerificationQueueView(View):
    """Admin dashboard listing organizations by verification status."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        if not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'Admin privileges required.'}, status=403)

        status_filter = request.GET.get('status', 'PENDING').upper()
        search_query = request.GET.get('q', '').strip()

        queryset = OrganizationProfile.objects.all().order_by('-updated_at')

        if status_filter in ['PENDING', 'APPROVED', 'REJECTED', 'DRAFT']:
            queryset = queryset.filter(verification_status=status_filter)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query) | queryset.filter(city__icontains=search_query)

        pending_count = OrganizationProfile.objects.filter(verification_status='PENDING').count()
        approved_count = OrganizationProfile.objects.filter(verification_status='APPROVED').count()
        rejected_count = OrganizationProfile.objects.filter(verification_status='REJECTED').count()

        return render(request, 'admin_verification/queue.html', {
            'organizations': queryset,
            'current_status': status_filter,
            'search_query': search_query,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
        })


class AdminOrganizationReviewDetailView(View):
    """Admin inspection view showing documents, eligibility, and approve/reject actions."""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request, org_id):
        if not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'Admin privileges required.'}, status=403)

        org = get_object_or_404(OrganizationProfile, id=org_id)
        reject_form = AdminOrganizationRejectForm()
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])

        # Check if all mandatory documents have at least one approved document
        can_approve = True
        missing_or_unapproved = []
        for req_type in required_types:
            has_app = org.documents.filter(document_type=req_type, review_status='APPROVED').exists()
            if not has_app:
                can_approve = False
                missing_or_unapproved.append(req_type.label)

        return render(request, 'admin_verification/review_detail.html', {
            'organization': org,
            'documents': org.documents.all(),
            'events': org.verification_events.all(),
            'reject_form': reject_form,
            'required_types': required_types,
            'can_approve': can_approve,
            'missing_or_unapproved': missing_or_unapproved,
        })


class AdminDocumentReviewActionView(View):
    """Admin action to review an individual document."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request, org_id, doc_id):
        if not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'Admin privileges required.'}, status=403)

        decision = request.POST.get('decision')
        rejection_reason = request.POST.get('rejection_reason', '')

        try:
            doc = DocumentService.review_document(request.user, doc_id, decision, rejection_reason)
            messages.success(request, f"Document '{doc.original_filename}' marked as {decision}.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('admin_organization_review', org_id=org_id)


class AdminOrganizationApproveActionView(View):
    """Admin action to approve organization."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request, org_id):
        if not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'Admin privileges required.'}, status=403)

        try:
            org = VerificationService.approve_organization(request.user, org_id)
            messages.success(request, f"Organization '{org.name}' has been verified and APPROVED.")
            return redirect('admin_verification_queue')
        except ConcurrencyConflictError as e:
            messages.error(request, f"Conflict: {str(e)}")
        except DjangoValidationError as e:
            msg = e.message_dict.get('documents', [str(e)])[0] if hasattr(e, 'message_dict') else str(e)
            messages.error(request, msg)
        except Exception as e:
            messages.error(request, str(e))

        return redirect('admin_organization_review', org_id=org_id)


class AdminOrganizationRejectActionView(View):
    """Admin action to reject organization."""

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request, org_id):
        if not request.user.is_admin_user:
            return render(request, '403.html', {'error_message': 'Admin privileges required.'}, status=403)

        rejection_reason = request.POST.get('rejection_reason', '').strip()
        if not rejection_reason:
            messages.error(request, "A specific rejection reason is required.")
            return redirect('admin_organization_review', org_id=org_id)

        try:
            org = VerificationService.reject_organization(request.user, org_id, rejection_reason)
            messages.warning(request, f"Organization '{org.name}' verification REJECTED with note.")
            return redirect('admin_verification_queue')
        except ConcurrencyConflictError as e:
            messages.error(request, f"Conflict: {str(e)}")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('admin_organization_review', org_id=org_id)
