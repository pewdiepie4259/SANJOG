from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # HTML / HTMX Routes
    path('organizations/onboarding/', views.onboarding_view, name='organization_onboarding'),
    path('organizations/create/', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('organizations/profile/', views.OrganizationProfileDetailView.as_view(), name='organization_profile'),
    path('organizations/profile/edit/', views.OrganizationProfileEditView.as_view(), name='organization_profile_edit'),
    path('organizations/submit/', views.OrganizationSubmitView.as_view(), name='organization_submit'),
    path('organizations/documents/', views.OrganizationDocumentManageView.as_view(), name='organization_documents'),
    path('organizations/documents/upload/', views.OrganizationDocumentUploadView.as_view(), name='organization_document_upload'),
    path('organizations/documents/<uuid:doc_id>/download/', views.OrganizationDocumentDownloadView.as_view(), name='organization_document_download'),
    path('organizations/documents/<uuid:doc_id>/delete/', views.OrganizationDocumentDeleteView.as_view(), name='organization_document_delete'),

    # Admin HTML / HTMX Routes
    path('admin/organizations/queue/', views.AdminVerificationQueueView.as_view(), name='admin_verification_queue'),
    path('admin/organizations/<uuid:org_id>/review/', views.AdminOrganizationReviewDetailView.as_view(), name='admin_organization_review'),
    path('admin/organizations/<uuid:org_id>/documents/<uuid:doc_id>/review/', views.AdminDocumentReviewActionView.as_view(), name='admin_document_review_action'),
    path('admin/organizations/<uuid:org_id>/approve/', views.AdminOrganizationApproveActionView.as_view(), name='admin_organization_approve_action'),
    path('admin/organizations/<uuid:org_id>/reject/', views.AdminOrganizationRejectActionView.as_view(), name='admin_organization_reject_action'),

    # REST API v1 Endpoints (/api/v1/)
    path('api/v1/organizations/me/', api_views.APIOrganizationMeView.as_view(), name='api_org_me'),
    path('api/v1/organizations/me/verification-status/', api_views.APIOrganizationVerificationStatusView.as_view(), name='api_org_verification_status'),
    path('api/v1/organizations/', api_views.APIOrganizationListCreateView.as_view(), name='api_org_create'),
    path('api/v1/organizations/<uuid:org_id>/', api_views.APIOrganizationDetailView.as_view(), name='api_org_detail'),
    path('api/v1/organizations/<uuid:org_id>/submit/', api_views.APIOrganizationSubmitView.as_view(), name='api_org_submit'),
    path('api/v1/organizations/<uuid:org_id>/documents/', api_views.APIOrganizationDocumentListCreateView.as_view(), name='api_org_documents'),
    path('api/v1/organizations/<uuid:org_id>/documents/<uuid:doc_id>/', api_views.APIOrganizationDocumentDetailView.as_view(), name='api_org_document_detail'),

    # Admin REST API v1 Endpoints
    path('api/v1/admin/organizations/', api_views.APIAdminOrganizationListView.as_view(), name='api_admin_org_list'),
    path('api/v1/admin/organizations/<uuid:org_id>/', api_views.APIAdminOrganizationDetailView.as_view(), name='api_admin_org_detail'),
    path('api/v1/admin/organizations/<uuid:org_id>/documents/<uuid:doc_id>/review/', api_views.APIAdminDocumentReviewView.as_view(), name='api_admin_document_review'),
    path('api/v1/admin/organizations/<uuid:org_id>/approve/', api_views.APIAdminOrganizationApproveView.as_view(), name='api_admin_org_approve'),
    path('api/v1/admin/organizations/<uuid:org_id>/reject/', api_views.APIAdminOrganizationRejectView.as_view(), name='api_admin_org_reject'),
]
