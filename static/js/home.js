
var settingsmenu = document.querySelector(".settings-menu");
var darkBtn = document.getElementById("dark-btn");

function settingsMenuToggle() {
  settingsmenu.classList.toggle("settings-menu-height");
}

// Fecha o menu de configurações ao clicar fora
document.addEventListener("mousedown", function(e) {
  if (settingsmenu && settingsmenu.classList.contains("settings-menu-height")) {
    // Se o clique não for dentro do menu nem no botão do usuário
    var userIcon = document.querySelector(".nav-user-icon");
    if (!settingsmenu.contains(e.target) && !userIcon.contains(e.target)) {
      settingsmenu.classList.remove("settings-menu-height");
    }
  }
});

darkBtn.onclick = function () {
  darkBtn.classList.toggle("dark-btn-on");
  document.body.classList.toggle("dark-theme");
};

if (localStorage.getItem("theme") == "light") {
  darkBtn.classList.remove("dark-btn-on");
  document.body.classList.remove("dark-theme");
} else if (localStorage.getItem("theme") == "dark") {
  darkBtn.classList.add("dark-btn-on");
  document.body.classList.add("dark-theme");
} else {
  localStorage.setItem("theme", "light");
}

const openModalBtn = document.getElementById("openPostModal");
const modal = document.getElementById("postModal");
const closeModalBtn = document.getElementById("closeModal");
const textarea = modal.querySelector("textarea");
const publishBtn = modal.querySelector(".publish-btn");

openModalBtn.addEventListener("click", () => {
  modal.style.display = "block";
});

closeModalBtn.addEventListener("click", () => {
  modal.style.display = "none";
  textarea.value = "";
  publishBtn.classList.remove("active");
  publishBtn.disabled = true;
});

window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
    textarea.value = "";
    publishBtn.classList.remove("active");
    publishBtn.disabled = true;
  }
});

textarea.addEventListener("input", () => {
  if (textarea.value.trim().length > 0) {
    publishBtn.disabled = false;
    publishBtn.classList.add("active");
  } else {
    publishBtn.disabled = true;
    publishBtn.classList.remove("active");
  }
});

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("click", function (e) {
  const btn = e.target.closest(".like-btn");
  if (!btn) return;

  const postId = btn.getAttribute("data-post-id");
  const url = `/feed/post/${postId}/like/`; // matches feed:toggle_like
  const csrftoken = getCookie("csrftoken");

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => {
      if (!res.ok) throw new Error("Network error");
      return res.json();
    })
    .then((data) => {
      // update count
      const countEl = document.getElementById(`like-count-${data.post_id}`);
      if (countEl) countEl.textContent = data.count;

      // toggle state
      if (data.liked) {
        btn.classList.add("liked");
        btn.setAttribute("aria-pressed", "true");
      } else {
        btn.classList.remove("liked");
        btn.setAttribute("aria-pressed", "false");
      }
    })
    .catch(() => {
      // optionally show a toast or fallback
      alert("Não foi possível curtir agora. Tente novamente.");
    });
});

// Toggle & load comments on first open
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".comment-btn");
  if (!btn) return;

  const postId = btn.dataset.postId;
  const panel = document.getElementById(`comments-panel-${postId}`);
  const list = document.getElementById(`comments-list-${postId}`);

  if (panel.hasAttribute("hidden")) {
    // Opening → fetch comments
    fetch(`/feed/post/${postId}/comments/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        list.innerHTML =
          data.comments.map(renderComment).join("") ||
          '<div class="comment-empty">Sem comentários ainda.</div>';
        panel.removeAttribute("hidden");
      })
      .catch(() => alert("Não foi possível carregar comentários."));
  } else {
    // Closing
    panel.setAttribute("hidden", "");
  }
});

function renderComment(c) {
  const title = c.user_title
    ? `<small class="comment-title">${c.user_title}</small>`
    : "";
  return `
    <div class="comment-item">
      <div class="comment-meta">
        <strong>${escapeHtml(c.user_fullname)}</strong> ${title}
        <span class="comment-date">${c.created}</span>
      </div>
      <div class="comment-body">${escapeHtml(c.body)}</div>
    </div>
  `;
}

// Submit new comment (event delegation)
document.addEventListener("submit", function (e) {
  const form = e.target.closest(".comment-form");
  if (!form) return;
  e.preventDefault();

  const postId = form.dataset.postId;
  const input = form.querySelector(".comment-input");
  const body = (input.value || "").trim();
  if (!body) return;

  const csrftoken = getCookie("csrftoken");
  fetch(`/feed/post/${postId}/comments/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ body }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        // append new comment
        const list = document.getElementById(`comments-list-${postId}`);
        list.insertAdjacentHTML("beforeend", renderComment(data.comment));

        // update count
        const countEl = document.getElementById(`comment-count-${postId}`);
        if (countEl) countEl.textContent = data.count;

        input.value = "";
      } else {
        alert(data.message || "Erro ao comentar.");
      }
    })
    .catch(() => alert("Não foi possível enviar o comentário."));
});

// Small helpers
function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// video control functions to stop and play automatically when video not on screen
document.addEventListener("DOMContentLoaded", function () {
  const videos = document.querySelectorAll("video");

  function pauseAllVideos(except = null) {
    videos.forEach((video) => {
      if (video !== except && !video.paused) {
        video.pause();
      }
    });
  }

  videos.forEach((video) => {
    video.addEventListener("play", () => pauseAllVideos(video));
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          entry.target.pause();
        }
      });
    },
    { threshold: 0.25 }
  );

  videos.forEach((video) => observer.observe(video));
});
