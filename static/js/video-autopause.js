/**
 * Video Auto-Pause Functionality
 * Automatically pauses videos when they scroll out of view
 */

class VideoAutoPause {
  constructor() {
    this.videos = [];
    this.scrollTimeout = null;
    this.init();
  }

  init() {
    // Wait for DOM to be ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.findVideos();
    this.bindEvents();
    this.checkVisibility(); // Initial check
  }

  findVideos() {
    // Find all videos in the document
    this.videos = Array.from(document.querySelectorAll("video"));

    // Also watch for dynamically added videos
    this.observeNewVideos();
  }

  observeNewVideos() {
    if (typeof MutationObserver !== "undefined") {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              // Element node
              // Check if the added node is a video
              if (node.tagName === "VIDEO") {
                this.videos.push(node);
              }
              // Check if the added node contains videos
              const childVideos = node.querySelectorAll
                ? node.querySelectorAll("video")
                : [];
              childVideos.forEach((video) => {
                if (!this.videos.includes(video)) {
                  this.videos.push(video);
                }
              });
            }
          });
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    }
  }

  bindEvents() {
    // Throttled scroll event
    window.addEventListener(
      "scroll",
      () => {
        clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => this.checkVisibility(), 100);
      },
      { passive: true }
    );

    // Check on resize
    window.addEventListener("resize", () => this.checkVisibility());

    // Check on orientation change (mobile)
    window.addEventListener("orientationchange", () => {
      setTimeout(() => this.checkVisibility(), 100);
    });
  }

  checkVisibility() {
    this.videos.forEach((video) => {
      if (this.isVideoInViewport(video)) {
        // Video is visible - we don't auto-play, but we allow manual play
        // You could add auto-play logic here if desired
      } else {
        // Video is not visible - pause it if playing
        if (!video.paused && !video.ended) {
          video.pause();
        }
      }
    });
  }

  isVideoInViewport(video) {
    const rect = video.getBoundingClientRect();
    const windowHeight =
      window.innerHeight || document.documentElement.clientHeight;
    const windowWidth =
      window.innerWidth || document.documentElement.clientWidth;

    // Check if any part of the video is visible
    const isVisible =
      rect.top < windowHeight &&
      rect.bottom > 0 &&
      rect.left < windowWidth &&
      rect.right > 0;

    // Optional: Only consider video visible if a certain percentage is in view
    // const visibleHeight = Math.min(rect.bottom, windowHeight) - Math.max(rect.top, 0);
    // const visibleWidth = Math.min(rect.right, windowWidth) - Math.max(rect.left, 0);
    // const visibleArea = visibleHeight * visibleWidth;
    // const totalArea = rect.height * rect.width;
    // const visibilityPercentage = visibleArea / totalArea;
    // return visibilityPercentage > 0.5; // At least 50% visible

    return isVisible;
  }

  // Public method to manually refresh video list
  refresh() {
    this.findVideos();
    this.checkVisibility();
  }

  // Public method to pause all videos
  pauseAll() {
    this.videos.forEach((video) => {
      if (!video.paused && !video.ended) {
        video.pause();
      }
    });
  }
}

// Initialize the video auto-pause functionality
// Use try-catch for production error handling
try {
  const videoAutoPause = new VideoAutoPause();

  // Expose globally for manual control if needed
  window.VideoAutoPause = VideoAutoPause;
  window.videoAutoPause = videoAutoPause;

  console.log("Video auto-pause initialized successfully");
} catch (error) {
  console.error("Failed to initialize video auto-pause:", error);
}
