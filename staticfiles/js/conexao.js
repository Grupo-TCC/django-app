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
  const btn = e.target.closest(".follow-btn");
  if (!btn) return;

  const url = btn.dataset.url; // ← use the real URL from Django
  const csrftoken = getCookie("csrftoken");

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.is_following) {
        btn.classList.add("following");
        btn.textContent = "Deixar de Seguir";
      } else {
        btn.classList.remove("following");
        btn.textContent = "Seguir";
      }
    });
});
