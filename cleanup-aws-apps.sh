#!/bin/bash

# InnovaSus AWS Cleanup Script
# Removes existing Amplify apps to start fresh

echo "🧹 InnovaSus AWS Cleanup"
echo "======================"

REGION="us-east-1"

echo "🔍 Checking existing Amplify apps..."

# Try to list apps
APPS=$(aws amplify list-apps --region $REGION --query 'apps[*].appId' --output text 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$APPS" ]; then
    echo "📋 Found existing apps:"
    aws amplify list-apps --region $REGION --query 'apps[*].[name,appId,defaultDomain]' --output table
    
    echo ""
    read -p "❓ Do you want to delete ALL Amplify apps? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️ Deleting apps..."
        
        for APP_ID in $APPS; do
            echo "   Deleting app: $APP_ID"
            aws amplify delete-app --app-id $APP_ID --region $REGION
            if [ $? -eq 0 ]; then
                echo "   ✅ Deleted: $APP_ID"
            else
                echo "   ❌ Failed to delete: $APP_ID"
            fi
        done
        
        echo ""
        echo "✅ Cleanup completed!"
    else
        echo "❌ Cleanup cancelled."
        exit 1
    fi
else
    echo "ℹ️ No existing apps found or insufficient permissions."
    echo "💡 Please delete apps manually via AWS Console:"
    echo "   https://console.aws.amazon.com/amplify/home"
fi

echo ""
echo "🎯 Ready for fresh InnovaSus deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Verify all apps are deleted in AWS Console"
echo "2. Run: ./deploy-innovasus-s3.sh"
echo "3. Or create new Amplify app manually"