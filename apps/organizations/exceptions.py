"""
Custom domain exceptions for SANJOG Organizations & Verification Pipeline.
"""

class ConcurrencyConflictError(Exception):
    """
    Raised when an organization verification decision conflicts with a concurrent
    decision already applied by another administrator.
    """
    pass

class DocumentValidationError(Exception):
    """
    Raised when a verification document fails security or content validation.
    """
    pass
