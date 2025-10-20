#!/bin/bash

# Production Deployment Script for Enhanced Video Features
# Run this script to properly deploy static files with Nginx + Gunicorn

echo "🚀 Deploying Enhanced Video Features for Production..."

# Step 1: Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Step 2: Verify all video files are in staticfiles
echo "🔍 Checking video files..."

JS_FILES=("feed-video.js")
CSS_FILES=("feed-video.css")

echo "📄 Checking JavaScript files..."
for file in "${JS_FILES[@]}"; do
    if [ -f "staticfiles/js/$file" ]; then
        echo "✅ $file found in staticfiles"
    else
        echo "❌ $file NOT found in staticfiles"
        echo "🔧 Copying manually..."
        mkdir -p staticfiles/js/
        cp "static/js/$file" "staticfiles/js/" 2>/dev/null || echo "⚠️  Could not copy $file"
    fi
done

echo "🎨 Checking CSS files..."
for file in "${CSS_FILES[@]}"; do
    if [ -f "staticfiles/css/$file" ]; then
        echo "✅ $file found in staticfiles"
    else
        echo "❌ $file NOT found in staticfiles"
        echo "🔧 Copying manually..."
        mkdir -p staticfiles/css/
        cp "static/css/$file" "staticfiles/css/" 2>/dev/null || echo "⚠️  Could not copy $file"
    fi
done

# Step 3: Set proper permissions
echo "🔐 Setting file permissions..."
chmod -R 755 staticfiles/
chown -R www-data:www-data staticfiles/ 2>/dev/null || echo "⚠️  Could not change ownership (run as root if needed)"

# Step 4: Test video file serving
echo "🧪 Testing video file serving..."
if [ -d "media" ]; then
    echo "✅ Media directory exists"
    chmod -R 755 media/
    chown -R www-data:www-data media/ 2>/dev/null || echo "⚠️  Could not change media ownership"
else
    echo "⚠️  Media directory not found"
fi

# Step 5: Create Nginx video configuration snippet
echo "📝 Creating Nginx video configuration..."
cat > nginx_video_config.txt << 'EOF'
# Add this to your Nginx server block for optimal video serving

# Video files location
location /media/ {
    alias /path/to/your/django/media/;
    
    # Enable range requests for video seeking
    add_header Accept-Ranges bytes;
    
    # Video-specific headers
    location ~* \.(mp4|webm|mov|avi|mkv)$ {
        add_header Cache-Control "public, max-age=2592000";
        add_header Accept-Ranges bytes;
        
        # Enable streaming
        mp4;
        mp4_buffer_size 1m;
        mp4_max_buffer_size 5m;
        
        # CORS headers for video
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS";
        add_header Access-Control-Allow-Headers "Range";
    }
}

# Static files
location /static/ {
    alias /path/to/your/django/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
EOF

# Step 6: Test file accessibility
echo "🧪 Testing file accessibility..."
echo "JavaScript files:"
for file in "${JS_FILES[@]}"; do
    if [ -f "staticfiles/js/$file" ]; then
        echo "✅ JS $file: $(du -h staticfiles/js/$file | cut -f1)"
    else
        echo "❌ JS $file: Not found"
    fi
done

echo "CSS files:"
for file in "${CSS_FILES[@]}"; do
    if [ -f "staticfiles/css/$file" ]; then
        echo "✅ CSS $file: $(du -h staticfiles/css/$file | cut -f1)"
    else
        echo "❌ CSS $file: Not found"
    fi
done

echo ""
echo "✨ Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your Nginx configuration with the snippet in nginx_video_config.txt"
echo "2. Test Nginx config: sudo nginx -t"
echo "3. Restart Gunicorn: sudo systemctl restart gunicorn"
echo "4. Reload Nginx: sudo systemctl reload nginx"
echo "5. Test video functionality on your production site"
echo ""
echo "🔧 Video Features Deployed:"
echo "  ✅ Auto-pause when scrolling out of view"
echo "  ✅ Enhanced video controls for longer videos"
echo "  ✅ Keyboard shortcuts (Space, Arrow keys, M, F)"
echo "  ✅ Better seeking and buffering"
echo "  ✅ Error handling and recovery"
echo ""
echo "🔍 Troubleshooting:"
echo "- Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "- Check Gunicorn logs: sudo journalctl -u gunicorn -f"
echo "- Test video serving: curl -I https://yoursite.com/media/path/to/video.mp4"
echo "- Check browser console for JavaScript errors"