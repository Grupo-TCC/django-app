const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});

// Toggle password visibility
function togglePassword(spanElement) {
  const input = spanElement.parentElement.querySelector('input');
  if (input) {
    if (input.type === 'password') {
      input.type = 'text';
      const icon = spanElement.querySelector('i');
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    } else {
      input.type = 'password';
      const icon = spanElement.querySelector('i');
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    }
  }
}