document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");
  const form = document.querySelector(".search-box");
  const container = document.querySelector(".community-container") || document.querySelector(".articles-list") || document.body;

  // Create or get the no-results message
  let noResultMsg = document.getElementById("no-results-message");
  if (!noResultMsg) {
    noResultMsg = document.createElement("p");
    noResultMsg.id = "no-results-message";
    noResultMsg.textContent = "Nenhum resultado encontrado.";
    noResultMsg.style.display = "none";
    noResultMsg.style.textAlign = "center";
    noResultMsg.style.color = "#888";
    noResultMsg.style.marginTop = "2rem";
    container.appendChild(noResultMsg);
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault(); // Prevent form submit
    });
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = this.value;
      const items = document.querySelectorAll(".searchable");
      let anyVisible = false;
      items.forEach((item) => {
        // Remove previous highlights
        const original = item.getAttribute('data-original-text');
        if (original) {
          item.innerHTML = original;
        } else {
          item.setAttribute('data-original-text', item.innerHTML);
        }
        const text = item.textContent;
        if (query && text.includes(query)) {
          // Highlight the match (case sensitive)
          const re = new RegExp(escapeRegExp(query), 'g');
          item.innerHTML = text.replace(re, '<mark>$&</mark>');
          item.style.display = "flex";
          anyVisible = true;
        } else if (!query) {
          item.style.display = "flex";
        } else {
          item.style.display = "none";
        }
      });
      noResultMsg.style.display = anyVisible || !query ? "none" : "block";
    });
  }
});
