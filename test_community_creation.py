#!/usr/bin/env python3
"""
Test script to create a community with an image
"""

import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Add the Django project to the path
sys.path.append('/Users/emersonokorie/Desktop/django-app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.auth import get_user_model
from feed.community_models import Community
from feed.forms import CommunityForm

def create_test_image():
    """Create a simple test image"""
    # Create a simple red image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return img_io.getvalue()

def test_community_creation():
    """Test creating a community with an image"""
    User = get_user_model()
    
    # Get the first user (or create one)
    user = User.objects.first()
    if not user:
        print("No users found. Please create a user first.")
        return
    
    print(f"Testing community creation with user: {user.username}")
    
    # Create test image data
    image_data = create_test_image()
    uploaded_file = SimpleUploadedFile(
        name='test_community_pic.jpg',
        content=image_data,
        content_type='image/jpeg'
    )
    
    # Test form with image
    form_data = {
        'name': 'Test Community with Image',
        'description': 'This is a test community with an image'
    }
    
    form = CommunityForm(data=form_data, files={'community_pic': uploaded_file})
    
    print(f"Form is valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
        return
    
    # Save the community
    community = form.save(commit=False)
    community.created_by = user
    community.save()
    community.members.add(user)
    
    print(f"Community created successfully: {community.name}")
    print(f"Community image URL: {community.get_community_picture_url()}")
    print(f"Community image path: {community.community_pic}")
    
    # Check if the file exists
    if community.community_pic:
        full_path = community.community_pic.path
        print(f"Image file exists: {os.path.exists(full_path)}")
        print(f"Image file path: {full_path}")

if __name__ == "__main__":
    try:
        test_community_creation()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()