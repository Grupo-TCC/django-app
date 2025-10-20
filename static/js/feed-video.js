/**
 * Complete Video Handler for feed-video class
 * Handles auto-pause, enhanced controls, and production deployment
 */

class FeedVideoHandler {
  constructor() {
    this.videos = [];
    this.scrollTimeout = null;
    this.init();
  }

  init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.findVideos();
    this.enhanceVideos();
    this.bindScrollEvents();
    this.observeNewVideos();
    console.log(
      "Feed video handler initialized with",
      this.videos.length,
      "videos"
    );
  }

  findVideos() {
    // Find all videos with feed-video class and regular video elements
    this.videos = Array.from(
      document.querySelectorAll("video.feed-video, video.post-img, video")
    );
  }

  enhanceVideos() {
    this.videos.forEach((video) => this.enhanceVideo(video));
  }

  enhanceVideo(video) {
    // Skip if already enhanced
    if (video.hasAttribute("data-enhanced")) return;

    video.setAttribute("data-enhanced", "true");

    // Ensure proper attributes for better control
    if (!video.hasAttribute("preload")) {
      video.preload = "metadata";
    }

    if (!video.hasAttribute("playsinline")) {
      video.setAttribute("playsinline", "");
    }

    // Add keyboard support
    this.addKeyboardControls(video);

    // Add enhanced loading and error handling
    this.addVideoEventHandlers(video);

    // Add click-to-seek functionality
    this.addClickToSeek(video);

    console.log("Enhanced video:", video.src || video.currentSrc);
  }

  addVideoEventHandlers(video) {
    // Loading states
    video.addEventListener("loadstart", () => {
      video.setAttribute("data-loading", "true");
      console.log("Video loading started:", video.src);
    });

    video.addEventListener("loadedmetadata", () => {
      video.removeAttribute("data-loading");
      console.log(
        "Video metadata loaded - Duration:",
        video.duration,
        "seconds"
      );

      // Enable seeking for longer videos
      if (video.duration > 0) {
        video.setAttribute("data-seekable", "true");
      }
    });

    video.addEventListener("loadeddata", () => {
      console.log("Video ready for playback");
    });

    video.addEventListener("canplay", () => {
      console.log("Video can start playing");
    });

    // Error handling
    video.addEventListener("error", (e) => {
      console.error("Video error:", e);
      this.handleVideoError(video, e);
    });

    // Seeking events
    video.addEventListener("seeking", () => {
      video.setAttribute("data-seeking", "true");
    });

    video.addEventListener("seeked", () => {
      video.removeAttribute("data-seeking");
    });

    // Stalled/suspended handling
    video.addEventListener("stalled", () => {
      console.log("Video stalled, attempting recovery...");
      this.handleStall(video);
    });

    // Progress tracking
    video.addEventListener("timeupdate", () => {
      if (video.duration > 0) {
        const progress = (video.currentTime / video.duration) * 100;
        video.setAttribute("data-progress", progress.toFixed(2));
      }
    });

    // Play/pause events
    video.addEventListener("play", () => {
      console.log("Video started playing");
    });

    video.addEventListener("pause", () => {
      console.log("Video paused");
    });
  }

  addKeyboardControls(video) {
    video.addEventListener("keydown", (e) => {
      // Only handle if video is focused
      if (document.activeElement !== video) return;

      switch (e.key) {
        case " ":
        case "k":
          e.preventDefault();
          this.togglePlayPause(video);
          break;
        case "ArrowLeft":
          e.preventDefault();
          this.safeSeek(video, Math.max(0, video.currentTime - 10));
          break;
        case "ArrowRight":
          e.preventDefault();
          this.safeSeek(
            video,
            Math.min(video.duration, video.currentTime + 10)
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          video.volume = Math.min(1, video.volume + 0.1);
          this.showVolumeIndicator(video, video.volume);
          break;
        case "ArrowDown":
          e.preventDefault();
          video.volume = Math.max(0, video.volume - 0.1);
          this.showVolumeIndicator(video, video.volume);
          break;
        case "m":
          e.preventDefault();
          video.muted = !video.muted;
          this.showMuteIndicator(video, video.muted);
          break;
        case "f":
          e.preventDefault();
          this.toggleFullscreen(video);
          break;
        case "0":
        case "1":
        case "2":
        case "3":
        case "4":
        case "5":
        case "6":
        case "7":
        case "8":
        case "9":
          e.preventDefault();
          const percentage = parseInt(e.key) * 10;
          this.safeSeek(video, (video.duration * percentage) / 100);
          break;
      }
    });

    // Make video focusable
    video.tabIndex = 0;
  }

  addClickToSeek(video) {
    video.addEventListener("click", (e) => {
      // Don't interfere with native controls
      if (e.target.closest("[controls]") && e.target !== video) return;

      const rect = video.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickPercent = clickX / rect.width;
      const newTime = clickPercent * video.duration;

      if (newTime >= 0 && newTime <= video.duration && video.duration > 0) {
        this.safeSeek(video, newTime);
        this.showSeekIndicator(video, newTime);
      }
    });
  }

  safeSeek(video, time) {
    try {
      if (video.readyState >= 2 && video.duration > 0) {
        const clampedTime = Math.max(0, Math.min(time, video.duration));
        video.currentTime = clampedTime;
        console.log("Seeked to:", clampedTime.toFixed(2), "seconds");
      } else {
        // Wait for metadata and try again
        video.addEventListener(
          "loadedmetadata",
          () => {
            const clampedTime = Math.max(0, Math.min(time, video.duration));
            video.currentTime = clampedTime;
          },
          { once: true }
        );
      }
    } catch (error) {
      console.error("Seek error:", error);
    }
  }

  togglePlayPause(video) {
    try {
      if (video.paused) {
        const playPromise = video.play();
        if (playPromise !== undefined) {
          playPromise.catch((error) => {
            console.error("Play failed:", error);
          });
        }
      } else {
        video.pause();
      }
    } catch (error) {
      console.error("Play/pause error:", error);
    }
  }

  toggleFullscreen(video) {
    try {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else if (video.requestFullscreen) {
        video.requestFullscreen();
      } else if (video.webkitRequestFullscreen) {
        video.webkitRequestFullscreen();
      } else if (video.mozRequestFullScreen) {
        video.mozRequestFullScreen();
      }
    } catch (error) {
      console.error("Fullscreen error:", error);
    }
  }

  // Auto-pause functionality
  bindScrollEvents() {
    window.addEventListener(
      "scroll",
      () => {
        clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => this.checkVideoVisibility(), 100);
      },
      { passive: true }
    );

    window.addEventListener("resize", () => this.checkVideoVisibility());
    window.addEventListener("orientationchange", () => {
      setTimeout(() => this.checkVideoVisibility(), 100);
    });

    // Initial check
    this.checkVideoVisibility();
  }

  checkVideoVisibility() {
    this.videos.forEach((video) => {
      const isVisible = this.isVideoInViewport(video);

      if (!isVisible && !video.paused && !video.ended) {
        video.pause();
        console.log("Auto-paused video (scrolled out of view)");
      }
    });
  }

  isVideoInViewport(video) {
    const rect = video.getBoundingClientRect();
    const windowHeight =
      window.innerHeight || document.documentElement.clientHeight;
    const windowWidth =
      window.innerWidth || document.documentElement.clientWidth;

    return (
      rect.top < windowHeight &&
      rect.bottom > 0 &&
      rect.left < windowWidth &&
      rect.right > 0
    );
  }

  // Visual feedback methods
  showVolumeIndicator(video, volume) {
    this.showIndicator(video, `Volume: ${Math.round(volume * 100)}%`);
  }

  showMuteIndicator(video, muted) {
    this.showIndicator(video, muted ? "Muted" : "Unmuted");
  }

  showSeekIndicator(video, time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    this.showIndicator(
      video,
      `${minutes}:${seconds.toString().padStart(2, "0")}`
    );
  }

  showIndicator(video, text) {
    // Remove existing indicator
    const existingIndicator =
      video.parentNode.querySelector(".video-indicator");
    if (existingIndicator) {
      existingIndicator.remove();
    }

    // Create new indicator
    const indicator = document.createElement("div");
    indicator.className = "video-indicator";
    indicator.textContent = text;
    indicator.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 5px 10px;
      border-radius: 4px;
      font-size: 14px;
      z-index: 100;
      pointer-events: none;
    `;

    // Position relative to video
    const videoRect = video.getBoundingClientRect();
    video.parentNode.style.position = "relative";
    video.parentNode.appendChild(indicator);

    // Auto-remove after 2 seconds
    setTimeout(() => {
      if (indicator.parentNode) {
        indicator.remove();
      }
    }, 2000);
  }

  // Error handling
  handleVideoError(video, error) {
    const errorCode = error.target?.error?.code || 0;
    const errorMessage = this.getErrorMessage(errorCode);

    console.error("Video error:", errorMessage);

    // Create error overlay
    const errorOverlay = document.createElement("div");
    errorOverlay.className = "video-error-overlay";
    errorOverlay.innerHTML = `
      <div class="error-content">
        <h4>⚠️ Erro no vídeo</h4>
        <p>${errorMessage}</p>
        <button onclick="this.closest('.video-error-overlay').remove(); this.closest('video').load();">
          🔄 Tentar novamente
        </button>
      </div>
    `;

    video.parentNode.insertBefore(errorOverlay, video.nextSibling);
  }

  getErrorMessage(code) {
    switch (code) {
      case 1:
        return "Download do vídeo foi interrompido pelo usuário.";
      case 2:
        return "Erro de rede ao carregar o vídeo.";
      case 3:
        return "Erro na decodificação do vídeo.";
      case 4:
        return "Formato de vídeo não suportado ou arquivo corrompido.";
      default:
        return "Erro desconhecido ao reproduzir o vídeo.";
    }
  }

  handleStall(video) {
    setTimeout(() => {
      if (video.readyState < 3 && !video.paused) {
        console.log("Attempting video recovery...");
        try {
          video.load();
        } catch (error) {
          console.error("Recovery failed:", error);
        }
      }
    }, 3000);
  }

  // Observer for dynamically added videos
  observeNewVideos() {
    if (typeof MutationObserver !== "undefined") {
      const observer = new MutationObserver((mutations) => {
        let hasNewVideos = false;

        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              if (node.tagName === "VIDEO") {
                this.enhanceVideo(node);
                this.videos.push(node);
                hasNewVideos = true;
              }
              const childVideos = node.querySelectorAll
                ? node.querySelectorAll("video")
                : [];
              childVideos.forEach((video) => {
                if (!this.videos.includes(video)) {
                  this.enhanceVideo(video);
                  this.videos.push(video);
                  hasNewVideos = true;
                }
              });
            }
          });
        });

        if (hasNewVideos) {
          console.log("New videos detected and enhanced");
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    }
  }

  // Public methods
  refresh() {
    this.findVideos();
    this.enhanceVideos();
    console.log("Video handler refreshed");
  }

  pauseAll() {
    this.videos.forEach((video) => {
      if (!video.paused && !video.ended) {
        video.pause();
      }
    });
    console.log("All videos paused");
  }

  getVideoInfo() {
    return this.videos.map((video) => ({
      src: video.src || video.currentSrc,
      duration: video.duration,
      currentTime: video.currentTime,
      paused: video.paused,
      muted: video.muted,
      volume: video.volume,
      readyState: video.readyState,
    }));
  }
}

// Initialize when DOM is ready
try {
  const feedVideoHandler = new FeedVideoHandler();

  // Expose globally for debugging and manual control
  window.FeedVideoHandler = FeedVideoHandler;
  window.feedVideoHandler = feedVideoHandler;

  console.log("✅ Feed Video Handler initialized successfully");
} catch (error) {
  console.error("❌ Failed to initialize Feed Video Handler:", error);
}
