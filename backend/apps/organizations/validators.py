import os
from pathlib import Path
from django.db import models
from django.core.exceptions import ValidationError

class OrganizationType(models.TextChoices):
    # Donor Types
    RESTAURANT = 'RESTAURANT', 'Restaurant'
    HOTEL = 'HOTEL', 'Hotel'
    HOSTEL_MESS = 'HOSTEL_MESS', 'Hostel Mess'
    CATERER = 'CATERER', 'Caterer'
    CANTEEN = 'CANTEEN', 'Canteen'
    EVENT_ORGANIZER = 'EVENT_ORGANIZER', 'Event Organizer'
    OTHER_DONOR = 'OTHER_DONOR', 'Other Donor Organization'

    # Receiver Types
    NGO = 'NGO', 'Non-Governmental Organization (NGO)'
    SHELTER = 'SHELTER', 'Shelter / Homeless Home'
    ORPHANAGE = 'ORPHANAGE', 'Orphanage'
    COMMUNITY_KITCHEN = 'COMMUNITY_KITCHEN', 'Community Kitchen'
    CHARITABLE_ORGANIZATION = 'CHARITABLE_ORGANIZATION', 'Charitable Trust / Organization'
    OTHER_RECEIVER = 'OTHER_RECEIVER', 'Other Receiver Organization'


DONOR_ORG_TYPES = [
    OrganizationType.RESTAURANT,
    OrganizationType.HOTEL,
    OrganizationType.HOSTEL_MESS,
    OrganizationType.CATERER,
    OrganizationType.CANTEEN,
    OrganizationType.EVENT_ORGANIZER,
    OrganizationType.OTHER_DONOR,
]

RECEIVER_ORG_TYPES = [
    OrganizationType.NGO,
    OrganizationType.SHELTER,
    OrganizationType.ORPHANAGE,
    OrganizationType.COMMUNITY_KITCHEN,
    OrganizationType.CHARITABLE_ORGANIZATION,
    OrganizationType.OTHER_RECEIVER,
]


class DocumentType(models.TextChoices):
    FSSAI_LICENSE = 'FSSAI_LICENSE', 'FSSAI Food Safety License'
    BUSINESS_REGISTRATION = 'BUSINESS_REGISTRATION', 'GST / Shop Act / Business Registration'
    NGO_DARPAN = 'NGO_DARPAN', 'NITI Aayog NGO Darpan Registration'
    TAX_EXEMPT_80G = 'TAX_EXEMPT_80G', '80G / 12A Tax Exemption Certificate'
    TRUST_DEED = 'TRUST_DEED', 'Trust Deed / Society Registration'
    ID_PROOF = 'ID_PROOF', 'Authorized Signatory Identity Proof'
    OTHER = 'OTHER', 'Other Supporting Accreditation'


# Configurable Mandatory Documents by Organization Type
REQUIRED_DOCUMENTS_BY_ORG_TYPE = {
    # Donors
    OrganizationType.RESTAURANT: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.HOTEL: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.HOSTEL_MESS: [DocumentType.FSSAI_LICENSE, DocumentType.ID_PROOF],
    OrganizationType.CATERER: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.CANTEEN: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.EVENT_ORGANIZER: [DocumentType.BUSINESS_REGISTRATION, DocumentType.ID_PROOF],
    OrganizationType.OTHER_DONOR: [DocumentType.BUSINESS_REGISTRATION],

    # Receivers
    OrganizationType.NGO: [DocumentType.NGO_DARPAN, DocumentType.TAX_EXEMPT_80G],
    OrganizationType.SHELTER: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.ORPHANAGE: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.COMMUNITY_KITCHEN: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.CHARITABLE_ORGANIZATION: [DocumentType.TRUST_DEED, DocumentType.TAX_EXEMPT_80G],
    OrganizationType.OTHER_RECEIVER: [DocumentType.TRUST_DEED],
}


# File Upload Boundaries
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_FILE_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp'}
PROHIBITED_EXTENSIONS = {
    '.svg', '.html', '.htm', '.xml', '.exe', '.bat', '.cmd', '.sh', 
    '.php', '.py', '.js', '.jar', '.vbs', '.msi', '.ps1'
}

# Canonical Binary Magic Signatures
MAGIC_SIGNATURES = {
    'pdf': b'%PDF-',
    'png': b'\x89PNG\r\n\x1a\n',
    'jpeg': b'\xff\xd8\xff',
    'webp': b'RIFF',  # Followed by WEBP at offset 8
}


def validate_organization_type_for_role(role, org_type):
    """
    Enforces that the selected organization type is valid for the user's operational role.
    Volunteers are forbidden from creating organizations.
    """
    if role == 'VOLUNTEER':
        raise ValidationError({'org_type': 'Rescue Volunteers operate individually and cannot register organizations.'})
    elif role == 'DONOR':
        if org_type not in DONOR_ORG_TYPES:
            raise ValidationError({'org_type': f"Invalid organization type '{org_type}' for Food Donor accounts. Must be one of {[c.label for c in DONOR_ORG_TYPES]}."})
    elif role == 'RECEIVER':
        if org_type not in RECEIVER_ORG_TYPES:
            raise ValidationError({'org_type': f"Invalid organization type '{org_type}' for Food Receiver accounts. Must be one of {[c.label for c in RECEIVER_ORG_TYPES]}."})
    elif role == 'ADMIN':
        pass  # Platform admin permitted to manage any organization
    else:
        raise ValidationError({'org_type': f"Unrecognized user operational role '{role}'."})


def validate_file_security(uploaded_file):
    """
    Deep binary file inspection:
    1. Size boundary checks (0 < size <= 5MB).
    2. Extension whitelisting & prohibited format blocking (SVG/HTML/executables).
    3. Magic byte signature verification.
    4. Extension-to-signature consistency verification.
    5. Defensive try/except buffer read with mandatory file seek reset.
    Returns detected canonical MIME content-type.
    """
    if not uploaded_file:
        raise ValidationError("No file was uploaded.")

    # 1. Size bounds
    file_size = getattr(uploaded_file, 'size', 0)
    if file_size <= 0:
        raise ValidationError("Uploaded file is empty (0 bytes).")
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of 5 MB.")

    filename = getattr(uploaded_file, 'name', '')
    ext = Path(filename).suffix.lower()

    # 2. Extension whitelisting
    if ext in PROHIBITED_EXTENSIONS or ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(f"File extension '{ext}' is not supported. Allowed formats: PDF, PNG, JPG, JPEG, WEBP.")

    # 3. Magic header byte inspection
    header_bytes = b''
    try:
        uploaded_file.seek(0)
        header_bytes = uploaded_file.read(512)
        uploaded_file.seek(0)  # Always reset seek pointer immediately
    except Exception as e:
        raise ValidationError(f"Failed to safely inspect file stream: {str(e)}")

    if len(header_bytes) < 4:
        raise ValidationError("File content is too small or malformed to verify.")

    # 4. Signature & Extension Consistency Check
    detected_mime = None
    if ext == '.pdf':
        if not header_bytes.startswith(MAGIC_SIGNATURES['pdf']):
            raise ValidationError("File content does not match the provided .pdf extension (invalid PDF header).")
        detected_mime = 'application/pdf'
    elif ext == '.png':
        if not header_bytes.startswith(MAGIC_SIGNATURES['png']):
            raise ValidationError("File content does not match the provided .png extension (invalid PNG header).")
        detected_mime = 'image/png'
    elif ext in ('.jpg', '.jpeg'):
        if not header_bytes.startswith(MAGIC_SIGNATURES['jpeg']):
            raise ValidationError("File content does not match the provided JPEG extension (invalid JPEG header).")
        detected_mime = 'image/jpeg'
    elif ext == '.webp':
        if not (header_bytes.startswith(MAGIC_SIGNATURES['webp']) and b'WEBP' in header_bytes[:16]):
            raise ValidationError("File content does not match the provided .webp extension (invalid WEBP header).")
        detected_mime = 'image/webp'
    else:
        raise ValidationError(f"Unsupported file format: {ext}")

    return detected_mime
