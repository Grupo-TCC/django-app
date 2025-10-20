# Complete Video Solution - Usage Guide

## 🎥 Your Video Element

```html
<video
  class="feed-video"
  src="{% static 'uploads/sample.mp4' %}"
  preload="metadata"
  controls
  muted
></video>
```

## ✨ Enhanced Version (Recommended)

```html
<div class="video-container">
  <video
    class="feed-video"
    src="{% static 'uploads/sample.mp4' %}"
    preload="metadata"
    controls
    muted
    playsinline
    data-video-id="unique-id-here"
  >
    <source src="{% static 'uploads/sample.mp4' %}" type="video/mp4" />
    <source src="{% static 'uploads/sample.webm' %}" type="video/webm" />
    <p>
      Seu navegador não suporta vídeo.
      <a href="{% static 'uploads/sample.mp4' %}">Baixar</a>
    </p>
  </video>
</div>
```

## 🚀 Features Included

### ✅ Auto-Pause on Scroll

- Videos automatically pause when scrolled out of view
- Saves bandwidth and improves performance
- Works on mobile and desktop

### ✅ Enhanced Controls for Longer Videos

- Better seeking functionality
- Click-to-seek anywhere on video
- Keyboard shortcuts support

### ✅ Keyboard Shortcuts

- `Space` or `K` - Play/Pause
- `←` - Seek backward 10s
- `→` - Seek forward 10s
- `↑` - Volume up
- `↓` - Volume down
- `M` - Toggle mute
- `F` - Toggle fullscreen
- `0-9` - Seek to percentage (0% to 90%)

### ✅ Error Handling

- Graceful error recovery
- User-friendly error messages
- Retry functionality

### ✅ Loading States

- Visual loading indicators
- Progress tracking
- Stall recovery

## 📁 Files Created

```
static/js/feed-video.js      # Main video handler
static/css/feed-video.css    # Video styles
templates/base.html          # Updated with includes
deploy-video-autopause.sh    # Production deployment
```

## 🔧 JavaScript API

```javascript
// Access the video handler
const videoHandler = window.feedVideoHandler;

// Get information about all videos
console.log(videoHandler.getVideoInfo());

// Pause all videos
videoHandler.pauseAll();

// Refresh video detection after DOM changes
videoHandler.refresh();

// Check if video handler is working
console.log("Videos found:", videoHandler.videos.length);
```

## 🎯 Production Deployment

### 1. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 2. Run Deployment Script

```bash
chmod +x deploy-video-autopause.sh
./deploy-video-autopause.sh
```

### 3. Update Nginx Configuration

Add to your Nginx server block:

```nginx
# Video files with range support
location /media/ {
    alias /path/to/your/django/media/;
    add_header Accept-Ranges bytes;

    location ~* \.(mp4|webm|mov|avi)$ {
        add_header Cache-Control "public, max-age=2592000";
        add_header Accept-Ranges bytes;

        # Enable MP4 streaming
        mp4;
        mp4_buffer_size 1m;
        mp4_max_buffer_size 5m;
    }
}

# Static files
location /static/ {
    alias /path/to/your/django/staticfiles/;
    expires 30d;
}
```

### 4. Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

## 🧪 Testing

### Manual Test

1. Load page with videos
2. Play a video
3. Scroll down (video should auto-pause)
4. Try keyboard shortcuts
5. Test seeking by clicking on video timeline

### Console Test

```javascript
// Check if everything loaded
console.log(window.feedVideoHandler);

// See all videos detected
console.log(feedVideoHandler.videos);

// Test auto-pause manually
feedVideoHandler.checkVideoVisibility();
```

## 📱 Mobile Support

- Touch-friendly controls
- Orientation change handling
- `playsinline` attribute for iOS
- Reduced motion support
- High contrast mode support

## 🐛 Troubleshooting

### Videos Not Auto-Pausing

- Check browser console for errors
- Verify `feed-video.js` is loaded
- Make sure videos have `feed-video` class

### Controls Not Working

- Ensure `preload="metadata"` is set
- Check video file format compatibility
- Verify video files are accessible

### Production Issues

- Run `collectstatic` command
- Check Nginx configuration for video serving
- Verify file permissions (755 for directories, 644 for files)
- Test video URL directly: `curl -I https://yoursite.com/static/js/feed-video.js`

### Common Fixes

```bash
# Fix permissions
chmod -R 755 staticfiles/
chmod -R 755 media/

# Test static file serving
python manage.py findstatic js/feed-video.js

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn nginx
```

## 🎨 Customization

### Custom Styles

Edit `/static/css/feed-video.css` to change appearance:

```css
.feed-video {
  border-radius: 12px; /* More rounded corners */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* Custom shadow */
}
```

### Custom Behavior

Edit `/static/js/feed-video.js` to modify functionality:

```javascript
// Change auto-pause threshold
isVideoInViewport(video) {
    // Only pause if 100% out of view (current)
    // Change logic here for different behavior
}
```

## ✅ Complete Solution Ready!

Your video system now includes:

- ✅ Auto-pause on scroll
- ✅ Enhanced controls for longer videos
- ✅ Keyboard shortcuts
- ✅ Error handling
- ✅ Production deployment
- ✅ Mobile optimization
- ✅ Accessibility support
