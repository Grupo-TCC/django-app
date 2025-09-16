document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase();
      const items = document.querySelectorAll(".searchable");

      items.forEach((item) => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? "flex" : "none";
      });
    });
  }
});
