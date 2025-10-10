#!/usr/bin/env python3
"""
Test script to check community form functionality
"""

import os
import sys
import django

# Add the Django project to the path
sys.path.append('/Users/emersonokorie/Desktop/django-app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from feed.forms import CommunityForm
from feed.community_models import Community
from django.core.files.uploadedfile import SimpleUploadedFile

def test_community_form():
    """Test the community form with and without image upload"""
    
    print("Testing CommunityForm functionality...")
    
    # Test 1: Form without image
    print("\n1. Testing form without image:")
    form_data = {
        'name': 'Test Community',
        'description': 'This is a test community description'
    }
    form = CommunityForm(data=form_data)
    print(f"Form is valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
    
    # Test 2: Check form fields
    print("\n2. Checking form fields:")
    form = CommunityForm()
    print(f"Form fields: {list(form.fields.keys())}")
    print(f"community_pic field type: {type(form.fields['community_pic'])}")
    print(f"community_pic required: {form.fields['community_pic'].required}")
    
    # Test 3: Check model field
    print("\n3. Checking model field:")
    community_model = Community()
    print(f"Model has community_pic field: {hasattr(community_model, 'community_pic')}")
    
    # Test 4: Check field attributes
    print("\n4. Checking field attributes:")
    field = Community._meta.get_field('community_pic')
    print(f"Field type: {type(field)}")
    print(f"Upload to: {field.upload_to}")
    print(f"Blank: {field.blank}")
    print(f"Null: {field.null}")

if __name__ == "__main__":
    test_community_form()