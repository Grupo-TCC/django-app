# Enhanced Video System Documentation

## Overview

This enhanced video system provides comprehensive video functionality including auto-pause, improved controls, and production-ready deployment for Nginx + Gunicorn environments.

### Features:

- **Auto-pause when scrolling** - Videos pause when they leave the viewport
- **Enhanced controls** - Better seeking and playback for longer videos
- **Keyboard shortcuts** - Full keyboard navigation support
- **Error handling** - Graceful error recovery and user feedback
- **Production optimized** - Configured for Nginx + Gunicorn deployment
- **Mobile responsive** - Touch-friendly and orientation-aware

### Benefits:

- **Saving bandwidth** - prevents videos from playing when not visible
- **Reducing distractions** - stops background audio from videos off-screen
- **Better performance** - reduces CPU/GPU usage for invisible videos
- **Mobile-friendly** - saves battery life on mobile devices
- **Improved UX** - Better controls for longer videos and seeking

## How It Works

### Automatic Detection

The script automatically finds and manages all video elements in the page, including:

- Existing videos on page load
- Dynamically added videos (via JavaScript)
- Videos in modals or dynamic content

### Scroll-Based Pausing

Videos are automatically paused when they completely leave the viewport:

- **Threshold**: Videos pause when they are completely out of view
- **Performance**: Uses throttled scroll events (100ms delay) for smooth performance
- **Responsive**: Also works on window resize and orientation changes

### Implementation Details

#### Files

- `/static/js/video-autopause.js` - Main functionality
- `/templates/base.html` - Global script inclusion

#### Key Features

1. **Intersection Observer Alternative**: Uses `getBoundingClientRect()` for maximum compatibility
2. **Performance Optimized**: Throttled event handlers prevent excessive calculations
3. **Dynamic Content Support**: Watches for new videos added via JavaScript
4. **Mobile Support**: Handles orientation changes
5. **Non-Intrusive**: Only pauses videos, never auto-plays them

#### Browser Compatibility

- ✅ All modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ Internet Explorer 11+ (with polyfills for older versions)

## Usage Examples

### Basic Video HTML

```html
<video controls class="post-img">
  <source src="video.mp4" type="video/mp4" />
  <source src="video.webm" type="video/webm" />
  Your browser doesn't support video.
</video>
```

### Dynamic Video Creation

```javascript
// Videos added dynamically are automatically detected
const video = document.createElement("video");
video.src = "new-video.mp4";
video.controls = true;
document.body.appendChild(video);
// Auto-pause will work for this video too!
```

### Manual Control

```javascript
// Pause all videos manually
window.videoAutoPause.pauseAll();

// Refresh video detection after major DOM changes
window.videoAutoPause.refresh();
```

## Configuration

### Visibility Threshold

The current implementation pauses videos when they are completely out of view. To modify this behavior, edit the `isVideoInViewport()` function in `video-autopause.js`:

```javascript
// Example: Require 50% visibility to keep playing
const visibleHeight =
  Math.min(rect.bottom, windowHeight) - Math.max(rect.top, 0);
const visibleWidth = Math.min(rect.right, windowWidth) - Math.max(rect.left, 0);
const visibleArea = visibleHeight * visibleWidth;
const totalArea = rect.height * rect.width;
const visibilityPercentage = visibleArea / totalArea;
return visibilityPercentage > 0.5; // At least 50% visible
```

### Throttle Timing

To adjust scroll performance, modify the timeout value:

```javascript
// In bindEvents() method
this.scrollTimeout = setTimeout(() => this.checkVisibility(), 50); // Faster response
```

## Current Implementation

The feature is currently active on:

- ✅ **Tradução page** (`templates/feed/traducao.html`) - Where videos are primarily displayed
- ✅ **All pages** (via `templates/base.html`) - Ready for future video content

## Testing

### Manual Testing

1. Navigate to the tradução page with video content
2. Start playing a video
3. Scroll so the video goes off-screen
4. ✅ Video should automatically pause
5. Scroll back to the video
6. ✅ Video remains paused (user can manually play again)

### Console Testing

Open browser developer tools and run:

```javascript
// Check if auto-pause is loaded
console.log(window.videoAutoPause);

// See all detected videos
console.log(window.videoAutoPause.videos);

// Manually trigger visibility check
window.videoAutoPause.checkVisibility();
```

## Future Enhancements

Possible improvements to consider:

1. **Smart Resume**: Remember play position and optionally resume when scrolling back
2. **Autoplay on Scroll**: Auto-play videos when they enter viewport (with user permission)
3. **Volume Control**: Gradually fade volume instead of immediate pause
4. **Analytics**: Track video engagement metrics
5. **Lazy Loading**: Defer video loading until they enter viewport
