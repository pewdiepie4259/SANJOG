from django.http import FileResponse, Http404
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsAdminUser

from .models import OrganizationProfile, OrganizationDocument
from .serializers import (
    OrganizationProfileSerializer,
    OrganizationDocumentSerializer,
    OrganizationCreateSerializer,
    AdminDocumentReviewSerializer,
    AdminOrganizationRejectSerializer
)
from .services import OrganizationService, DocumentService, VerificationService
from .exceptions import ConcurrencyConflictError
from .permissions import IsOrganizationOwner, IsOwnerOrAdmin


class APIOrganizationMeView(APIView):
    """API Endpoint: Fetch current authenticated user's organization profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return Response({'detail': 'No organization profile found for this account.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationProfileSerializer(request.user.organization_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIOrganizationListCreateView(APIView):
    """API Endpoint: Register a new organization profile for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                org = OrganizationService.create_profile(
                    user=request.user,
                    **serializer.validated_data
                )
                return Response(OrganizationProfileSerializer(org).data, status=status.HTTP_201_CREATED)
            except DjangoValidationError as e:
                return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIOrganizationDetailView(APIView):
    """API Endpoint: Retrieve or update organization profile details."""
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        if org.user != request.user and not request.user.is_admin_user:
            return Response({'detail': 'You do not have permission to view this organization.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(OrganizationProfileSerializer(org).data, status=status.HTTP_200_OK)

    def patch(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        if org.user != request.user:
            return Response({'detail': 'You do not have permission to modify this organization.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            updated_org = OrganizationService.update_profile(request.user, org.id, **request.data)
            return Response(OrganizationProfileSerializer(updated_org).data, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class APIOrganizationSubmitView(APIView):
    """API Endpoint: Submit organization for administrative verification."""
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        if org.user != request.user:
            return Response({'detail': 'You do not have permission to submit this organization.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            submitted_org = OrganizationService.submit_for_verification(request.user, org.id)
            return Response({
                'message': 'Organization profile successfully submitted for verification.',
                'organization': OrganizationProfileSerializer(submitted_org).data
            }, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class APIOrganizationVerificationStatusView(APIView):
    """API Endpoint: Retrieve verification status and rejection commentary."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'organization_profile'):
            return Response({'detail': 'No organization profile found.'}, status=status.HTTP_404_NOT_FOUND)
        org = request.user.organization_profile
        return Response({
            'organization_id': org.id,
            'name': org.name,
            'verification_status': org.verification_status,
            'verification_status_display': org.get_verification_status_display(),
            'rejection_reason': org.rejection_reason,
            'verified_at': org.verified_at,
            'is_verified': org.is_verified,
        }, status=status.HTTP_200_OK)


class APIOrganizationDocumentListCreateView(APIView):
    """API Endpoint: List documents or upload a new verification document."""
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        if org.user != request.user and not request.user.is_admin_user:
            return Response({'detail': 'You do not have permission to view documents for this organization.'}, status=status.HTTP_403_FORBIDDEN)
        documents = org.documents.all()
        return Response(OrganizationDocumentSerializer(documents, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        if org.user != request.user:
            return Response({'detail': 'You do not have permission to upload documents for this organization.'}, status=status.HTTP_403_FORBIDDEN)

        document_type = request.data.get('document_type')
        uploaded_file = request.FILES.get('file')

        if not document_type:
            return Response({'document_type': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file:
            return Response({'file': ['No file uploaded.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = DocumentService.upload_document(request.user, org.id, document_type, uploaded_file)
            return Response(OrganizationDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class APIOrganizationDocumentDetailView(APIView):
    """API Endpoint: Securely download binary file or delete draft/rejected document."""
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id, doc_id):
        doc = get_object_or_404(OrganizationDocument, id=doc_id, organization_id=org_id)
        if doc.organization.user != request.user and not request.user.is_admin_user:
            return Response({'detail': 'You do not have permission to access this document.'}, status=status.HTTP_403_FORBIDDEN)

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

    def delete(self, request, org_id, doc_id):
        doc = get_object_or_404(OrganizationDocument, id=doc_id, organization_id=org_id)
        if doc.organization.user != request.user:
            return Response({'detail': 'You do not have permission to delete this document.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            DocumentService.delete_document(request.user, doc.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class APIAdminDocumentReviewView(APIView):
    """API Endpoint: Admin individual document review (APPROVE or REJECT)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, org_id, doc_id):
        doc = get_object_or_404(OrganizationDocument, id=doc_id, organization_id=org_id)
        serializer = AdminDocumentReviewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                reviewed_doc = DocumentService.review_document(
                    admin_user=request.user,
                    document_id=doc.id,
                    decision=serializer.validated_data['decision'],
                    rejection_reason=serializer.validated_data.get('rejection_reason', '')
                )
                return Response(OrganizationDocumentSerializer(reviewed_doc).data, status=status.HTTP_200_OK)
            except DjangoValidationError as e:
                return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIAdminOrganizationListView(APIView):
    """API Endpoint: Admin list and filter organizations by verification status and city."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = OrganizationProfile.objects.all().order_by('-created_at')

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(verification_status=status_param.upper())

        org_type_param = request.query_params.get('org_type')
        if org_type_param:
            queryset = queryset.filter(org_type=org_type_param.upper())

        city_param = request.query_params.get('city')
        if city_param:
            queryset = queryset.filter(city__icontains=city_param.strip())

        serializer = OrganizationProfileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAdminOrganizationDetailView(APIView):
    """API Endpoint: Admin inspect complete organization profile and audit history."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        serializer = OrganizationProfileSerializer(org)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAdminOrganizationApproveView(APIView):
    """API Endpoint: Admin approve pending organization following document check."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, org_id):
        try:
            approved_org = VerificationService.approve_organization(request.user, org_id)
            return Response({
                'message': 'Organization successfully verified and approved.',
                'organization': OrganizationProfileSerializer(approved_org).data
            }, status=status.HTTP_200_OK)
        except ConcurrencyConflictError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
        except DjangoValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class APIAdminOrganizationRejectView(APIView):
    """API Endpoint: Admin reject pending organization with mandatory rejection notes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, org_id):
        serializer = AdminOrganizationRejectSerializer(data=request.data)
        if serializer.is_valid():
            try:
                rejected_org = VerificationService.reject_organization(
                    admin_user=request.user,
                    org_id=org_id,
                    rejection_reason=serializer.validated_data['rejection_reason']
                )
                return Response({
                    'message': 'Organization verification rejected.',
                    'organization': OrganizationProfileSerializer(rejected_org).data
                }, status=status.HTTP_200_OK)
            except ConcurrencyConflictError as e:
                return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
            except DjangoValidationError as e:
                return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
