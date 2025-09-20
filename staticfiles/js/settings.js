document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("id_profile_picture");

  if (input) {
    input.style.display = "none"; // hide ugly file input

    input.addEventListener("change", function () {
      if (this.files.length > 0) {
        this.form.submit(); // auto-submit when file selected
      }
    });
  }
});
