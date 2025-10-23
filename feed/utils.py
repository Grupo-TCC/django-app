"""
Utility functions for the feed app
"""
from django.contrib.auth.models import User

def get_regular_users():
    """
    Returns a queryset of regular users (excludes superusers and staff).
    Use this for any public user listings in the application.
    """
    return User.objects.filter(
        is_active=True,
        email_verified=True,
        is_superuser=False,
        is_staff=False
    )

def get_regular_users_except(exclude_user):
    """
    Returns a queryset of regular users excluding a specific user.
    Commonly used for listing users other than the current user.
    """
    return get_regular_users().exclude(id=exclude_user.id)