#!/bin/bash

echo "🔍 Diagnosing Video Functionality Issues"
echo "========================================="

# Check if files exist
echo "📁 Checking file existence..."

FILES_TO_CHECK=(
    "static/js/feed-video.js"
    "static/css/feed-video.css"
    "templates/base.html"
    "templates/video-test.html"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "🌐 Testing Django server..."

# Check if Django server is running
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "✅ Django server is running"
    
    # Test static file access
    echo "📄 Testing static file access..."
    
    # Test CSS file
    if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000/static/css/feed-video.css" | grep -q "200"; then
        echo "✅ CSS file accessible"
    else
        echo "❌ CSS file not accessible"
    fi
    
    # Test JS file  
    if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000/static/js/feed-video.js" | grep -q "200"; then
        echo "✅ JS file accessible"
    else
        echo "❌ JS file not accessible"
    fi
    
    # Test video test page
    if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000/feed/video-test/" | grep -q "200"; then
        echo "✅ Video test page accessible"
        echo "🚀 Visit: http://127.0.0.1:8000/feed/video-test/"
    else
        echo "❌ Video test page not accessible"
    fi
    
else
    echo "❌ Django server not running"
    echo "💡 Start server with: python manage.py runserver"
fi

echo ""
echo "🔧 Checking Django settings..."

# Check Django settings for static files
if python manage.py diffsettings | grep -q "STATIC_URL"; then
    echo "✅ STATIC_URL configured"
else
    echo "❌ STATIC_URL not configured"
fi

echo ""
echo "📊 File contents check..."

# Check if JavaScript file has basic structure
if grep -q "class FeedVideoHandler" static/js/feed-video.js 2>/dev/null; then
    echo "✅ JavaScript class structure found"
else
    echo "❌ JavaScript class structure missing"
fi

# Check if CSS file has basic styles
if grep -q ".feed-video" static/css/feed-video.css 2>/dev/null; then
    echo "✅ CSS styles found"
else
    echo "❌ CSS styles missing"
fi

echo ""
echo "🧪 Quick JavaScript syntax check..."
node -c static/js/feed-video.js 2>/dev/null && echo "✅ JavaScript syntax valid" || echo "❌ JavaScript syntax error"

echo ""
echo "💡 Troubleshooting Tips:"
echo "1. Visit http://127.0.0.1:8000/feed/video-test/ to test functionality"
echo "2. Open browser developer tools (F12) to check for errors"
echo "3. Check Network tab for failed file loads"
echo "4. Run 'python manage.py collectstatic' if using production settings"
echo "5. Check console output for JavaScript errors"