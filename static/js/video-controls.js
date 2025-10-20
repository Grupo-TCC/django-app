/**
 * Enhanced Video Controls Handler
 * Fixes video control issues for longer videos
 * Ensures proper seeking, loading, and playback
 */

class EnhancedVideoControls {
  constructor() {
    this.videos = [];
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
    this.observeNewVideos();
  }

  findVideos() {
    this.videos = Array.from(document.querySelectorAll("video"));
  }

  enhanceVideos() {
    this.videos.forEach((video) => this.enhanceVideo(video));
  }

  enhanceVideo(video) {
    // Skip if already enhanced
    if (video.hasAttribute("data-enhanced")) return;

    video.setAttribute("data-enhanced", "true");

    // Force metadata loading for proper controls
    video.preload = "metadata";

    // Enable seeking for longer videos
    video.addEventListener("loadstart", () => {
      console.log("Video loading started:", video.src);
    });

    video.addEventListener("loadedmetadata", () => {
      console.log("Video metadata loaded:", {
        duration: video.duration,
        videoWidth: video.videoWidth,
        videoHeight: video.videoHeight,
      });

      // Force browser to recognize the video as seekable
      if (video.duration && video.duration > 0) {
        video.setAttribute("data-duration", video.duration);
        this.fixSeekingIssues(video);
      }
    });

    video.addEventListener("loadeddata", () => {
      console.log("Video data loaded, ready for playback");
      this.enableCustomControls(video);
    });

    video.addEventListener("error", (e) => {
      console.error("Video error:", e);
      this.handleVideoError(video, e);
    });

    // Handle seeking issues
    video.addEventListener("seeking", () => {
      video.setAttribute("data-seeking", "true");
    });

    video.addEventListener("seeked", () => {
      video.removeAttribute("data-seeking");
    });

    // Prevent common issues with longer videos
    video.addEventListener("stalled", () => {
      console.log("Video stalled, attempting recovery...");
      this.handleStall(video);
    });

    video.addEventListener("suspend", () => {
      console.log("Video loading suspended");
    });

    // Handle timeupdate for proper progress
    video.addEventListener("timeupdate", () => {
      if (video.duration && video.duration > 0) {
        const progress = (video.currentTime / video.duration) * 100;
        video.setAttribute("data-progress", progress);
      }
    });
  }

  fixSeekingIssues(video) {
    // Create a more reliable seeking mechanism
    const originalSeek = video.currentTime;

    // Add custom seek handling
    video.addEventListener("click", (e) => {
      if (e.target === video && !e.target.closest(".video-controls")) {
        // Calculate click position for seeking
        const rect = video.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercent = clickX / rect.width;
        const newTime = clickPercent * video.duration;

        if (newTime >= 0 && newTime <= video.duration) {
          this.safeSek(video, newTime);
        }
      }
    });
  }

  safeSeek(video, time) {
    try {
      // Ensure the video is ready for seeking
      if (video.readyState >= 2 && video.duration > 0) {
        video.currentTime = Math.max(0, Math.min(time, video.duration));
      } else {
        // Wait for metadata and try again
        video.addEventListener(
          "loadedmetadata",
          () => {
            video.currentTime = Math.max(0, Math.min(time, video.duration));
          },
          { once: true }
        );
      }
    } catch (error) {
      console.error("Seek error:", error);
    }
  }

  enableCustomControls(video) {
    // Add keyboard shortcuts
    video.addEventListener("keydown", (e) => {
      switch (e.key) {
        case " ":
        case "k":
          e.preventDefault();
          this.togglePlayPause(video);
          break;
        case "ArrowLeft":
          e.preventDefault();
          this.safeSeek(video, video.currentTime - 10);
          break;
        case "ArrowRight":
          e.preventDefault();
          this.safeSeek(video, video.currentTime + 10);
          break;
        case "ArrowUp":
          e.preventDefault();
          video.volume = Math.min(1, video.volume + 0.1);
          break;
        case "ArrowDown":
          e.preventDefault();
          video.volume = Math.max(0, video.volume - 0.1);
          break;
        case "m":
          e.preventDefault();
          video.muted = !video.muted;
          break;
        case "f":
          e.preventDefault();
          this.toggleFullscreen(video);
          break;
      }
    });

    // Make video focusable for keyboard controls
    video.tabIndex = 0;
  }

  togglePlayPause(video) {
    try {
      if (video.paused) {
        video.play().catch((error) => {
          console.error("Play failed:", error);
        });
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

  handleVideoError(video, error) {
    const errorMessage = this.getErrorMessage(error);
    console.error("Video error:", errorMessage);

    // Create error overlay
    const errorOverlay = document.createElement("div");
    errorOverlay.className = "video-error-overlay";
    errorOverlay.innerHTML = `
      <div class="error-content">
        <h4>Erro no vídeo</h4>
        <p>${errorMessage}</p>
        <button onclick="location.reload()">Tentar novamente</button>
      </div>
    `;

    // Insert after video
    video.parentNode.insertBefore(errorOverlay, video.nextSibling);
  }

  getErrorMessage(error) {
    const code = error.target?.error?.code || error.code;
    switch (code) {
      case 1:
        return "Download do vídeo foi interrompido.";
      case 2:
        return "Erro de rede ao carregar o vídeo.";
      case 3:
        return "Erro na decodificação do vídeo.";
      case 4:
        return "Formato de vídeo não suportado.";
      default:
        return "Erro desconhecido no vídeo.";
    }
  }

  handleStall(video) {
    // Try to recover from stalled state
    setTimeout(() => {
      if (video.readyState < 3) {
        try {
          video.load(); // Reload the video
        } catch (error) {
          console.error("Recovery failed:", error);
        }
      }
    }, 3000);
  }

  observeNewVideos() {
    if (typeof MutationObserver !== "undefined") {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              if (node.tagName === "VIDEO") {
                this.enhanceVideo(node);
                this.videos.push(node);
              }
              const childVideos = node.querySelectorAll
                ? node.querySelectorAll("video")
                : [];
              childVideos.forEach((video) => {
                if (!this.videos.includes(video)) {
                  this.enhanceVideo(video);
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

  // Public method to refresh all videos
  refresh() {
    this.findVideos();
    this.enhanceVideos();
  }
}

// Initialize enhanced video controls
const enhancedVideoControls = new EnhancedVideoControls();

// Expose globally
window.EnhancedVideoControls = EnhancedVideoControls;
window.enhancedVideoControls = enhancedVideoControls;
