var settingsmenu = document.querySelector(".settings-menu");
var darkBtn = document.getElementById("dark-btn");

function settingsMenuToggle() {
  settingsmenu.classList.toggle("settings-menu-height");
}

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
